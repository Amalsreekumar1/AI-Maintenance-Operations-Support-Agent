import pandas as pd 

#file_path = "data\injection_molding_qa_cleaned.csv"

def build_chunks(file_path):
    df = pd.read_csv(file_path)
    chunks = []
    for index, row in df.iterrows():
        chunk = {
            'id': index,
            'question': row['Questions'],
            'text': row['Answers']
        }
        chunks.append(chunk)

    return chunks