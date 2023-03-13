import subprocess

JOB_NUM = 1
ELEMS_PER_JOB = 10
MAX_ELEMS = 1000
PROCESSED_ELEMS = 0


def load_sites():
    command_load_sites = f"tail -n +{(JOB_NUM - 1) * ELEMS_PER_JOB + 1} top-1m.csv | head -n {ELEMS_PER_JOB} > test.csv"
    subprocess.check_call(command_load_sites, shell=True)


load_sites()

# Open a file for reading
with open('test.csv', 'r') as f:
    # Read the contents of the file into a variable
    file_contents = f.read()

# Split the contents of the file into a list of lines
lines = file_contents.split('\n')
sites = {}

# Loop over each line and print it
for line in lines:
    if line.strip():
        # print(line)
        site_rank, site = line.split(",")
        if "://" not in site:
            site = "http://" + site
        # print(f'site = {site}, rank = {site_rank}')
        sites[site_rank] = site

print(sites)