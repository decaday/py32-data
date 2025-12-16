import os
import re
import sys
import yaml

def get_rcc_h_define(file_path):
    rcc_info = {}

    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return {}

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        h_file = file.read().replace(" \\\n", "")

    for line in h_file.splitlines():
        if "__HAL_RCC_" in line:
            
            if "_FORCE_RESET" in line and "SET_BIT" in line:
                match = re.search('__HAL_RCC_(.*)_FORCE_RESET', line)
                if match:
                    device_name = match.group(1)

                    # Extract the two variables within the SET_BIT function
                    variables_match = re.search(r'SET_BIT\((.*?), (.*?)\)', line)
                    if variables_match:
                        variables = variables_match.groups()
                        register = variables[0].split('->')[-1].strip()
                        field = variables[1].split('_')[-1].strip()

                        if device_name not in rcc_info:
                            rcc_info[device_name] = {}
                        
                        rcc_info[device_name]["reset"] = {
                            "register": register,
                            "field": field
                        }

            elif "_CLK_ENABLE()" in line and "SET_BIT" in line:
                match = re.search('__HAL_RCC_(.*)_CLK_', line)
                if match:
                    device_name = match.group(1)
                    
                    # Extract the two variables within the SET_BIT function
                    variables_match = re.search(r'SET_BIT\((.*?), (.*?)\)', line)
                    if variables_match:
                        variables = variables_match.groups()
                        register = variables[0].split('->')[-1].strip()
                        field = variables[1].split('_')[-1].strip()

                        if device_name not in rcc_info:
                            rcc_info[device_name] = {}

                        rcc_info[device_name]["enable"] = {
                            "register": register,
                            "field": field
                        }

    return rcc_info

if __name__ == "__main__":
    header_path = "xxx/header/py32f0xx_hal_rcc.h"
    output_path = "data/dies/rcc/DIE030.yaml"

    if len(sys.argv) >= 2:
        header_path = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]

    data = get_rcc_h_define(header_path)

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, default_flow_style=False, sort_keys=True)

    print(f"RCC YAML generated at: {output_path}")