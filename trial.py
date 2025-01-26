import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from datetime import timedelta

# Function to convert time strings to timedelta
def time_to_timedelta(time_str):
    try:
        minutes, seconds = map(float, time_str.split(':'))
        return timedelta(minutes=minutes, seconds=seconds)
    except:
        return timedelta(0)

# Create a Tkinter root window (it will remain hidden)
root = Tk()
root.withdraw()

# Open a dialog to select the input Excel file
excel_file_path = askopenfilename(title="Select Excel File", filetypes=[("Excel files", "*.xls")])
if not excel_file_path:
    print("No file selected. Exiting...")
    exit()

# Open a dialog to select the save location for the output TXT file
txt_file_path = asksaveasfilename(title="Save TXT File", defaultextension=".txt", filetypes=[("Text files", "*.txt")])
if not txt_file_path:
    print("No file location selected. Exiting...")
    exit()

# Open a dialog to select the save location for the output LIF file
lif_file_path = asksaveasfilename(title="Save LIF File", defaultextension=".lif", filetypes=[("LIF files", "*.lif")])
if not lif_file_path:
    print("No file location selected. Exiting...")
    exit()

# Load the "Places" sheet from the selected Excel file
df = pd.read_excel(excel_file_path, sheet_name="Places", header=1)

# Drop any rows where the Position or Bib columns are missing or not integers
df = df.dropna(subset=['Position', 'Bib'])

# Convert 'Position' and 'Bib' columns to integers, and drop rows with invalid data
df['Position'] = pd.to_numeric(df['Position'], errors='coerce').dropna().astype(int)
df['Bib'] = pd.to_numeric(df['Bib'], errors='coerce').dropna().astype(int)

# Filter out rows where 'Position' or 'Bib' is still NaN after conversion
df = df.dropna(subset=['Position', 'Bib'])

# Split Name column into first and last names
df[['first name', 'last name']] = df['Name'].str.split(' ', 1, expand=True)

# Sort the dataframe by Position
df = df.sort_values('Position').reset_index(drop=True)

# Add placeholder columns for the LIF file
df['lane'] = 1  # or any default value
df['license'] = ''
df['delta time'] = ''
df['ReacTime'] = ''
df['splits'] = ''
df['time trial start time'] = ''
df['user 1'] = ''
df['user 2'] = ''
df['user 3'] = ''

# Initialize 'Score' column as object type
df['Score'] = None

# Calculate team scores
team_scores = {}
team_counts = {}
team_times = {}
team_total_times = {}

for index, row in df.iterrows():
    team = row['Team']
    if team not in team_counts:
        team_counts[team] = 0
        team_scores[team] = 0
        team_times[team] = []
        team_total_times[team] = timedelta(0)
    
    team_counts[team] += 1

    # Only score the first 7 runners, and only count the first 5 runners for scoring
    if team_counts[team] <= 7:
        if team_counts[team] <= 5:
            team_scores[team] += row['Position']
            df.at[index, 'Score'] = row['Position']
            team_total_times[team] += time_to_timedelta(row['Time'])
        else:
            df.at[index, 'Score'] = None  # Indicate the runner doesn't score

        team_times[team].append(row['Position'])

# Convert total time to a readable format
for team in team_total_times:
    total_time = team_total_times[team]
    minutes = int(total_time.total_seconds() // 60)
    seconds = int(total_time.total_seconds() % 60)
    team_total_times[team] = f"{minutes}:{seconds:02d}"

# Print team scores
for team, score in team_scores.items():
    print(f"Team {team} total score: {score}")

# Save to the specified LIF file
lif_df = df[['Position', 'Bib', 'lane', 'last name', 'first name', 'Team', 'Time', 'license', 'delta time', 'ReacTime', 'splits', 'time trial start time', 'user 1', 'user 2', 'user 3']]
lif_df.to_csv(lif_file_path, index=False)
print(f"LIF file saved to {lif_file_path}")

# Prepare the dataframe for export to TXT file
df['Name'] = df['first name'] + ' ' + df['last name']
export_df = df[['Position', 'Name', 'Grade', 'Bib', 'Team', 'Score', 'Time']]

# Create a formatted TXT file
with open(txt_file_path, 'w') as txt_file:
    txt_file.write("="*80 + "\n")
    txt_file.write("  Pl Athlete                 Yr   #  Team                      Score       Time \n")
    txt_file.write("="*80 + "\n")
    
    for _, row in export_df.iterrows():
        pl = f"{row['Position']:>4}"
        athlete = f"{row['Name']:<20}"
        yr = f"{row['Grade']:>4}"
        bib = f"{row['Bib']:>4}"
        team = f"{row['Team']:<25}"
        score = f"{'' if pd.isna(row['Score']) else row['Score']:>6}"
        time = f"{row['Time']:>10}"
        
        txt_file.write(f" {pl} {athlete} {yr} {bib} {team} {score} {time} \n")
    
    txt_file.write("\nRank Team Score Total 1 2 3 4 5 6 7 \n")
    txt_file.write("="*80 + "\n")
    
    # Rank teams by their score
    ranked_teams = sorted(team_scores.items(), key=lambda x: x[1])
    rank = 1
    for team, score in ranked_teams:
        places = ' '.join(map(str, team_times[team]))
        total_time = team_total_times[team]
        txt_file.write(f" {rank} {team:<20} {score:<4} {total_time:<8} {places}\n")
        rank += 1

print(f"TXT file saved to {txt_file_path}")
