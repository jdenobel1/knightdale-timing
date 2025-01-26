import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import timedelta

# Function to convert time strings to timedelta
def time_to_timedelta(time_str):
    try:
        minutes, seconds = map(float, time_str.split(':'))
        return timedelta(minutes=minutes, seconds=seconds)
    except:
        return timedelta(0)

# Function to process scoring output
def scoring_output():
    try:
        # Open a dialog to select the input Excel file
        excel_file_path = filedialog.askopenfilename(title="Select Excel File", filetypes=[("Excel files", "*.xls")])
        if not excel_file_path:
            messagebox.showerror("Error", "No Excel file selected. Exiting...")
            return

        # Open a dialog to select the save location for the output TXT file
        txt_file_path = filedialog.asksaveasfilename(title="Save TXT File", defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not txt_file_path:
            messagebox.showerror("Error", "No TXT file location selected. Exiting...")
            return

        # Open a dialog to select the save location for the output LIF file
        lif_file_path = filedialog.asksaveasfilename(title="Save LIF File", defaultextension=".lif", filetypes=[("LIF files", "*.lif")])
        if not lif_file_path:
            messagebox.showerror("Error", "No LIF file location selected. Exiting...")
            return

        # Load the "Places" sheet from the selected Excel file
        df = pd.read_excel(excel_file_path, sheet_name="Places", header=1)

        # Drop any rows where the Position or Bib columns are missing or not integers
        df = df.dropna(subset=['Position', 'Bib'])
        df['Position'] = pd.to_numeric(df['Position'], errors='coerce').dropna().astype(int)
        df['Bib'] = pd.to_numeric(df['Bib'], errors='coerce').dropna().astype(int)
        df = df.dropna(subset=['Position', 'Bib'])

        # Split Name column into first and last names
        df[['first name', 'last name']] = df['Name'].str.split(' ', 1, expand=True)

        # Convert Grade to integer
        df['Grade'] = df['Grade'].astype(int)

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

        # Save to the specified LIF file
        lif_df = df[['Position', 'Bib', 'lane', 'last name', 'first name', 'Team', 'Time', 'license', 'delta time', 'ReacTime', 'splits', 'time trial start time', 'user 1', 'user 2', 'user 3']]
        lif_df.to_csv(lif_file_path, index=False)

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

        messagebox.showinfo("Success", f"Scoring output saved to {txt_file_path} and {lif_file_path}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while processing the scoring output: {e}")

# Create the main GUI
def create_gui():
    root = tk.Tk()
    root.title("Scoring Output Processor")

    tk.Label(root, text="Scoring Output Processor", font=("Arial", 16)).pack(pady=10)

    tk.Button(root, text="Process Scoring Output", command=scoring_output).pack(pady=20)
    tk.Button(root, text="Quit", command=root.quit).pack(pady=20)

    root.mainloop()

# Run the GUI
create_gui()
