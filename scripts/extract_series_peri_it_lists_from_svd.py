import os
import glob
import yaml
import xml.etree.ElementTree as ET

def extract_svd_lists(svd_dir, output_base_dir):
    # Pattern to match files ending with "xx.svd"
    # Logic: The asterisk (*) in the user request represents the series name
    search_pattern = os.path.join(svd_dir, "*xx.svd")
    svd_files = glob.glob(search_pattern)

    if not svd_files:
        print(f"No SVD files found matching pattern '{search_pattern}'")
        return

    # Ensure output directories exist
    peri_out_dir = os.path.join(output_base_dir, "series", "peripheral_lists")
    int_out_dir = os.path.join(output_base_dir, "series", "interrupt_lists")
    
    os.makedirs(peri_out_dir, exist_ok=True)
    os.makedirs(int_out_dir, exist_ok=True)

    for file_path in svd_files:
        filename = os.path.basename(file_path)
        
        # Extract series name by removing the trailing "xx.svd"
        # Example: "PY32F030xx.svd" -> "PY32F030"
        series_name = filename[:-6]

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            print(f"Failed to parse {filename}: {e}")
            continue

        peripherals_list = []
        interrupts_set = set()

        # Iterate over all defined peripherals
        for peripheral in root.findall(".//peripheral"):
            # Extract peripheral name
            name_elem = peripheral.find('name')
            if name_elem is not None:
                peripherals_list.append(name_elem.text)

            # Extract interrupt names associated with this peripheral
            for interrupt in peripheral.findall('interrupt'):
                int_name_elem = interrupt.find('name')
                if int_name_elem is not None:
                    interrupts_set.add(int_name_elem.text)

        # Write Peripheral List to YAML
        peri_output_path = os.path.join(peri_out_dir, f"{series_name}.yaml")
        with open(peri_output_path, 'w', encoding='utf-8') as f:
            # Saving list as is (usually follows address order in SVD)
            yaml.dump(peripherals_list, f, default_flow_style=False)

        # Write Interrupt List to YAML
        int_output_path = os.path.join(int_out_dir, f"{series_name}.yaml")
        with open(int_output_path, 'w', encoding='utf-8') as f:
            # Convert set to sorted list for deterministic output
            yaml.dump(sorted(list(interrupts_set)), f, default_flow_style=False)

        print(f"Generated lists for: {series_name}")

if __name__ == "__main__":
    svd_directory = "svd"
    data_directory = "data"

    extract_svd_lists(svd_directory, data_directory)