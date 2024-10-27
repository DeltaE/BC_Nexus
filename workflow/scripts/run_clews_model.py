# %%
# %matplotlib inline

# %%
import argparse,yaml
import subprocess
from bc_combined_modelling import linking_utility as utils
from bc_combined_modelling import clews_builder

# %%
def main(
    config_file_path:str
):  
    config=utils.load_config(config_file_path)# Extract CSV file paths from YAML
    
    n_clusters = config['CLUSTERING']['n_clusters']
    hour_grouping = config['CLUSTERING']['hour_grouping']
    days_in_year = config['CLUSTERING']['days_in_year']
    start_year = config['GENERAL']['start_year']
    last_year = config['GENERAL']['last_year']
    StorageMaxCapacity = config['STORAGE']['BATTERY']['storage_max_capacity']
    ResidualStorageCapacity = config['STORAGE']['BATTERY']['residual_storage_capacity']
    input_csv_dir = config['FILES']['input_csv_directory']
    input_CF_wind_file = config['FILES']['DATA']['data_8760']['CF_wind']
    input_CF_solar_file = config['FILES']['DATA']['data_8760']['CF_solar']
    input_SDP_file = config['FILES']['DATA']['data_8760']['SDP']
    input_CF_csv_file = config['FILES']['capacity_factor_8760_file']
    input_SDP_csv_file = config['FILES']['specified_demand_profile_8760_file']

    output_CF_csv_file = config['FILES']['capacity_factor_file']
    output_SDP_csv_file = config['FILES']['specified_demand_profile_file']
    output_timeslice_csv_file = config['FILES']['timeslice_file']
    output_daytype_csv_file = config['FILES']['daytype_file']
    output_yearsplit_csv_file = config['FILES']['yearsplit_file']

    cases = config['CASES']
    
### CLUSTERING
    representative_days, chronological_sequence = clews_builder.cluster_data(input_CF_wind_file, input_CF_solar_file, input_SDP_file, n_clusters)
    print(f"Representative days: {representative_days}")

### MATHS

    # Number of blocks per day based on the hour grouping
    blocks_per_day = 24 // hour_grouping
    # Total timeslices considering the representative days
    timeslices = len(representative_days) * blocks_per_day
    # Chronological timeslices is number of days in year * blocks per day. If hourly analysis, chronological timeslice is 8760
    chronological_timeslices = days_in_year * blocks_per_day
    daytypes = len(representative_days)
    year_split = 1 / timeslices
    day_split = hour_grouping / (24 * 365)

### UPDATING CAPACITY FACTOR AND SPECIFIED DEMAND PROFILE

    # Updating capacity factor (averaging the values)
    clews_builder.CFandSDP(input_CF_csv_file, representative_days, hour_grouping, output_CF_csv_file, operation='mean')
    clews_builder.replication(output_CF_csv_file, start_year, last_year, group_by='TECHNOLOGY')

    # Updating specified demand profile (summing the values)
    clews_builder.CFandSDP(input_SDP_csv_file, representative_days, hour_grouping, output_SDP_csv_file, operation='sum')
    clews_builder.replication(output_SDP_csv_file, start_year, last_year, group_by='FUEL')

### UPDATING TIMESLICE AND DAYTYPE
    # Updating timeslice
    # %%
    clews_builder.new_list(timeslices, output_timeslice_csv_file)

    # Updating daytype
    clews_builder.new_list(daytypes, output_daytype_csv_file)

### UPDATING YEARSPLIT
    # %%
    clews_builder.yearsplit(timeslices, representative_days,  chronological_sequence, days_in_year, start_year, output_yearsplit_csv_file)
    clews_builder.replication(output_yearsplit_csv_file, start_year, last_year)

### UPDATING KOTZUR STRUCTURE AND RUNNING MODELS

    for case_name, case_info in cases.items():

        ### Copying CSV files
        input_csv_case_dir = case_info['input_otoole_csv']['directory']
        clews_builder.copy_csv_files(input_csv_dir, input_csv_case_dir)

        ### Skip if case_name is 'Niet'
        # if case_name == 'Model_Niet':
        #     continue

        ### Updating Model Kotzur
        if case_name == 'Model_Kotzur':
            print(f"Updating case: {case_name}")
            
            # Updating dayscro
            output_dayscro_csv_file = case_info['input_otoole_csv']['dayscro']
            clews_builder.new_list(days_in_year, output_dayscro_csv_file)
            
            # Updating conversionld
            output_conversionld_csv_file = case_info['input_otoole_csv']['conversionld']
            clews_builder.conversionld(timeslices, len(representative_days), output_conversionld_csv_file)

            # Updating conversionldc
            output_conversionldc_csv_file = case_info['input_otoole_csv']['conversionldc']
            clews_builder.conversion(chronological_sequence, representative_days, days_in_year, output_conversionldc_csv_file)

            # Updating day split in yaml file
            otoole_yaml_file = case_info['otoole_config']
            clews_builder.new_yaml_param(otoole_yaml_file, 'DaySplit', day_split)
        
### Updating otoole yaml file
        otoole_yaml_file = case_info['otoole_config']
        clews_builder.new_yaml_param(otoole_yaml_file, 'StorageMaxCapacity', StorageMaxCapacity)
        clews_builder.new_yaml_param(otoole_yaml_file, 'ResidualStorageCapacity', ResidualStorageCapacity)

        # Creating txt from csv using otoole
        output_txt_file = case_info['output_otoole_txt']
        print(f"Converting csv to txt with otoole for case: {case_name}")
        command_otoole = f"otoole convert csv datafile {input_csv_case_dir} {output_txt_file} {otoole_yaml_file}"
        subprocess.run(command_otoole, shell=True, text=True)

        # Preprocessing 
        output_model_file = case_info['model_file']
        otoole_preprocessing_script = case_info['preprocessing_script']
        output_model_file_preprocessed = case_info['model_file_preprocessed']
        output_txt_file_preprocessed = case_info['output_otoole_txt_processed']
        otoole_results=case_info['results']
        
        print(f"Preprocessing case: {case_name}")
        command_preprocess = f"python {otoole_preprocessing_script} {output_txt_file} {output_txt_file_preprocessed} {output_model_file} {output_model_file_preprocessed}"
        subprocess.run(command_preprocess, shell=True, text=True)

### Running model
        # data_glp_path = case_info['data_glp']
        data_sol_path = case_info['data_sol']
        # data_sol_cbc_path = case_info['data_sol_cbc']
        LP_file = case_info['LP_file']
        
        print(f"Running case: {case_name}")
        
### Write LP with GLPSOL
        # command_run = f"glpsol -m {output_model_file_preprocessed} -d {output_txt_file_preprocessed} --wglp {data_glp_path} --write {data_sol_path}"  
        # subprocess.run(command_run, shell=True, text=True)
        
        print(f"Creating LP file: {LP_file} from \nModel : {output_model_file_preprocessed} \nDatafile: {output_txt_file_preprocessed}")

        cmd_lp_create= f"glpsol -m {output_model_file_preprocessed} -d {output_txt_file_preprocessed} --wlp {LP_file} --check"
        subprocess.run(cmd_lp_create, shell=True, text=True)
        
        # cmd_cbc_model_run= f"cbc {LP_file} solve -solu {data_sol_cbc_path}"
        # subprocess.run(cmd_cbc_model_run, shell=True, text=True)
        
### Solve the LP with GUROBI Solver
        print(f"Running Gurobi Solver with LP file: {LP_file} and the targeted ResultFile: {data_sol_path}")
        cmd_solve_model_gurobi= f"gurobi_cl ResultFile={data_sol_path} {LP_file}"
        subprocess.run(cmd_solve_model_gurobi, shell=True, text=True)
        
### Extract the CSV results from GUROBI Solution/Result datafile
        print(f"Initiating otoole to extract results from Gurobi Solver using Datafile : {output_txt_file} , config file: {otoole_yaml_file}")
        otoole_results = f"otoole results gurobi csv {data_sol_path} {otoole_results} datafile {output_txt_file} {otoole_yaml_file}"
        subprocess.run(otoole_results, shell=True, text=True)
        print(f"Result extraction completed.")
    
    return
    
# %%

if __name__ == "__main__":
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Run data preparation script')
    parser.add_argument('config', type=str, help=f"Path to the configuration file 'config_master.yml'")
    
    # Parse the arguments
    args = parser.parse_args()
    main(args.config)
    
    #----------------------- for notebook run/Debugging------------------------------------
    # config_file_path='config/config_master.yml'
    # main(config_file_path)
