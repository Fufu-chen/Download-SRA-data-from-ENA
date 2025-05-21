import os
import requests
import subprocess

input_file = "SRA_Accession.txt"
output_dir = "Output"
os.makedirs(output_dir, exist_ok=True)

with open(input_file) as f:
    lines = f.readlines()[1:]  # skip head
    for line in lines:
        sra_id = line.strip().split()[1]
        print(f"Processing {sra_id}...")

        url = f"https://www.ebi.ac.uk/ena/portal/api/filereport?accession={sra_id}&result=read_run&fields=fastq_ftp"
        r = requests.get(url)
        if r.status_code != 200:
            print(f"❌ Failed to query {sra_id}")
            continue

        lines = r.text.strip().split("\n")
        if len(lines) < 2:
            print(f"❌ No fastq links found for {sra_id}")
            continue

        # Extract the second column
        data_line = lines[1].strip().split("\t")
        if len(data_line) < 1:
            print(f"❌ Malformed line for {sra_id}: {lines[1]}")
            continue

        ftp_links = data_line[-1].split(";")  
        for link in ftp_links:
            full_link = "ftp://" + link.strip()
            print(f"  → Downloading {full_link}")
            result = subprocess.run(["wget", "-c", "-P", output_dir, full_link])
            if result.returncode != 0:
                print(f"❌ Download failed: {full_link}")
