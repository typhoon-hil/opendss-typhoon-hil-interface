if __name__ == "__main__":

    import sys
    import pathlib
    sys.path.append(f"{pathlib.Path(__file__).parent.joinpath('importer_files')}")
    from importer_files.convert_to_tse import convert_to_tse

    try:
        passed_arguments = sys.argv

        if len(passed_arguments) != 3:
            print("Arguments missing.")

        else:
            this_file = passed_arguments[0]
            dss_file_path = pathlib.Path(passed_arguments[1])
            component_placement_mode = passed_arguments[2]
            if component_placement_mode == "1":
                mode = "charge-spring"
            elif component_placement_mode == "2":
                mode = "center-expanding"

            if dss_file_path.is_file():

                if mode not in ("charge-spring", "center-expanding"):
                    print("Invalid placement mode.")
                else:
                    out_folder = pathlib.Path(__file__).parent.joinpath('output_files')
                    if not out_folder.is_dir():
                        out_folder.mkdir(parents=True)
                    out_path = out_folder.joinpath(f'{dss_file_path.stem}.tse')

                    convert_to_tse(
                        dss_file_path=dss_file_path,
                        output_path=out_path,
                        auto_place_mode=mode,
                    )
            else:
                print(f"File not found: {str(dss_file_path)}")

    except Exception as catch_all:
        print(f"ERROR: {catch_all}")