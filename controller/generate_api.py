from api.v1.types import StaticRoute
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-path",
        help="Output CRD files to specified folder path, else use current folder",
        default=".",
    )
    args = parser.parse_args()

    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)
    with open(f"{args.output_path}/crd.yaml", "w") as file:
        file.writelines(StaticRoute.crd_schema())
