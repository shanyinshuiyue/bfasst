#!/usr/bin/python3

import argparse
import glob
import pathlib

import bfasst

def main():
    parser = argparse.ArgumentParser()

    designs = []
    for directory in bfasst.EXAMPLES_PATH.rglob('*'):
        if (directory / "design.yaml").is_file():
            designs.append(str(directory.relative_to(bfasst.EXAMPLES_PATH)))

    parser.add_argument("design_path", choices = designs, help = "Path to design, relative to examples directory.")
    parser.add_argument("flow", choices=[e.value for e in bfasst.flow.Flows])
    parser.add_argument("--force", action='store_true')
    error_flows = []
    for dir_item in bfasst.ERROR_FLOW_PATH.iterdir():
        if (bfasst.EXPERIMENTS_PATH / dir_item).is_file() and dir_item.suffix == ".yaml":
            error_flows.append(dir_item.stem)
    parser.add_argument("--error_flow", choices = error_flows, help = "YAML file describing errors to inject for testing. Only works with flows designed for error injection")
    args = parser.parse_args()

    # Load the design
    design = bfasst.design.Design(args.design_path)

    # Create temp folder
    build_dir = pathlib.Path.cwd() / "build" / args.flow / args.design_path
    if not build_dir.is_dir():
        build_dir.mkdir(parents=True)
    elif not args.force:
        bfasst.utils.error("Build directory", build_dir, "already exists.  Use --force to overwrite")
    else:
        pass
        # bfasst.utils.clean_folder(build_dir)

    # Store the error flow for later
    if args.error_flow:
        design.error_flow_yaml = args.error_flow + ".yaml"

    # Get the flow object
    for flow_itr in bfasst.flow.Flows:
        if args.flow == flow_itr.value:
            flow = flow_itr
            break
    
    # Run the design
    #status = bfasst.flow.run_flow(design, bfasst.flow.Flows.IC2_LSE_CONFORMAL, build_dir)
    status = bfasst.flow.run_flow(design, flow, build_dir)

    print(status)


if __name__ == "__main__":
    main()
