#Parts of the code in this model were generated with the assistance of AI and subsequently revised and validated by the author.
import os
import sys
import argparse
import pandas as pd
import numpy as np
import pulp


def load_data(user_path: str, fac_path: str,
              user_id_col: str = "user_id",
              fac_id_col: str = "facility_id",
              weight_col: str = "demand"):
    users = pd.read_csv(user_path)
    facilities = pd.read_csv(fac_path)

    # Validate required columns
    for col in [user_id_col, "x", "y"]:
        if col not in users.columns:
            raise ValueError(f"users.csv is missing required column: {col}")
    for col in [fac_id_col, "x", "y"]:
        if col not in facilities.columns:
            raise ValueError(f"facilities.csv is missing required column: {col}")

    # Weight column (default = 1.0)
    if weight_col in users.columns:
        users["_weight"] = users[weight_col].fillna(1.0).astype(float)
    else:
        users["_weight"] = 1.0

    users = users.copy().reset_index(drop=True)
    facilities = facilities.copy().reset_index(drop=True)
    return users, facilities, user_id_col, fac_id_col


def euclidean_dist_matrix(users: pd.DataFrame, facilities: pd.DataFrame) -> np.ndarray:
    uxy = users[["x", "y"]].to_numpy(dtype=float)
    fxy = facilities[["x", "y"]].to_numpy(dtype=float)
    diff = uxy[:, None, :] - fxy[None, :, :]
    return np.sqrt((diff ** 2).sum(axis=2))  # [U, F]


def solve_p_median(users: pd.DataFrame, facilities: pd.DataFrame,
                   p: int, fac_id_col: str) -> dict:
    U, F = users.shape[0], facilities.shape[0]
    if not (1 <= p <= F):
        raise ValueError(f"p must be in [1, {F}] (got p={p}).")

    D = euclidean_dist_matrix(users, facilities)     # U x F
    W = users["_weight"].to_numpy(dtype=float)       # U

    prob = pulp.LpProblem("P_Median", pulp.LpMinimize)

    x = pulp.LpVariable.dicts("x",
                              ((u, f) for u in range(U) for f in range(F)),
                              lowBound=0, upBound=1, cat=pulp.LpBinary)
    y = pulp.LpVariable.dicts("y",
                              (f for f in range(F)),
                              lowBound=0, upBound=1, cat=pulp.LpBinary)

    # Objective
    prob += pulp.lpSum(W[u] * D[u, f] * x[(u, f)] for u in range(U) for f in range(F))

    # Constraints
    for u in range(U):
        prob += pulp.lpSum(x[(u, f)] for f in range(F)) == 1, f"user_assign_{u}"
    for u in range(U):
        for f in range(F):
            prob += x[(u, f)] <= y[f], f"open_link_u{u}_f{f}"
    prob += pulp.lpSum(y[f] for f in range(F)) == p, "open_exactly_p"

    # Solve
    solver = pulp.PULP_CBC_CMD(msg=False)
    result_status = prob.solve(solver)
    status_str = pulp.LpStatus[result_status]
    if status_str != "Optimal":
        raise RuntimeError(f"Optimization did not reach optimality (status: {status_str}).")

    open_idx = [f for f in range(F) if pulp.value(y[f]) > 0.5]

    assign_f, assign_dist = [], []
    for u in range(U):
        vals = np.array([pulp.value(x[(u, f)]) for f in range(F)])
        f_star = int(vals.argmax())
        assign_f.append(f_star)
        assign_dist.append(D[u, f_star])

    total_cost = float(pulp.value(prob.objective))
    return {
        "status": status_str,
        "total_cost": total_cost,
        "open_index_list": open_idx,
        "open_facility_ids": facilities.loc[open_idx, fac_id_col].tolist(),
        "assign_facility_index": assign_f,
        "assign_dist": assign_dist,
    }


def ensure_parent_dir(path: str):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def export_results(selected_path: str, assignments_path: str,
                   users: pd.DataFrame, facilities: pd.DataFrame,
                   user_id_col: str, fac_id_col: str,
                   solution: dict):
    # 1) Selected facilities
    sel = facilities.loc[solution["open_index_list"], [fac_id_col, "x", "y"]].copy()
    sel["opened"] = 1
    ensure_parent_dir(selected_path)
    sel.to_csv(selected_path, index=False, encoding="utf-8-sig")

    # 2) User assignments
    assign_df = users[[user_id_col, "x", "y", "_weight"]].copy()
    assign_df.rename(columns={"_weight": "weight"}, inplace=True)
    f_idx = solution["assign_facility_index"]
    assign_df["assigned_facility_id"] = [facilities.loc[i, fac_id_col] for i in f_idx]
    assign_df["distance"] = solution["assign_dist"]
    assign_df["weighted_distance"] = assign_df["weight"] * assign_df["distance"]
    ensure_parent_dir(assignments_path)
    assign_df.to_csv(assignments_path, index=False, encoding="utf-8-sig")

    print("[OK] Results exported:")
    print(f"  Selected facilities -> {selected_path}")
    print(f"  Assignments         -> {assignments_path}")


def main():
    parser = argparse.ArgumentParser(
        description="p-median solver (weights + facility count p), customizable output filenames"
    )
    parser.add_argument("--users", required=True,
                        help="Path to users CSV (columns: user_id,x,y,[demand])")
    parser.add_argument("--facilities", required=True,
                        help="Path to facilities CSV (columns: facility_id,x,y)")
    parser.add_argument("--p", type=int, required=True,
                        help="Number of facilities to open (p)")
    parser.add_argument("--out_dir", default="./out",
                        help="Output directory used when filenames are not explicitly provided")

    # Optional column names
    parser.add_argument("--user_id_col", default="user_id",
                        help="Users ID column name (default: user_id)")
    parser.add_argument("--facility_id_col", default="facility_id",
                        help="Facilities ID column name (default: facility_id)")
    parser.add_argument("--weight_col", default="demand",
                        help="Users weight column name (default: demand; if missing, weight=1)")

    # New: customizable output filenames or full paths
    parser.add_argument("--selected_file", default="",  # if empty -> use out_dir/selected_facilities.csv
                        help="Filename or full path for selected facilities CSV")
    parser.add_argument("--assignments_file", default="",  # if empty -> use out_dir/assignments.csv
                        help="Filename or full path for assignments CSV")

    args = parser.parse_args()

    users, facilities, user_id_col, fac_id_col = load_data(
        args.users, args.facilities, args.user_id_col, args.facility_id_col, args.weight_col
    )

    solution = solve_p_median(users, facilities, args.p, fac_id_col)

    # Resolve output paths
    selected_path = args.selected_file if args.selected_file else os.path.join(args.out_dir, "facilities.csv")
    assignments_path = args.assignments_file if args.assignments_file else os.path.join(args.out_dir, "assignments.csv")

    export_results(selected_path, assignments_path, users, facilities, user_id_col, fac_id_col, solution)

    print(f"Status = {solution['status']}")
    print(f"Total weighted distance = {solution['total_cost']:.6f}")
    print(f"Opened facilities (IDs) = {solution['open_facility_ids']}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
