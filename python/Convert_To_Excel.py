import pandas as pd

def read_data(file_path):
    with open(file_path, 'r') as f:
        data = f.readlines()
    return data

def convert_to_excel(data, output_file):
    df = pd.DataFrame.from_dict(data=eval(''.join(data)))
    df.to_excel(output_file, index=False)

def main():
    file_path = 'python/data/TOTAL_JUN_AUG_AVIS.json'
    output_file = 'python/data/Excel/TOTAL_JUN_AUG_AVIS.xlsx'
    
    convert_to_excel(read_data(file_path), output_file)
    
if __name__ == '__main__':
    main()
    