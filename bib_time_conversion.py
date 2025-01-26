import tkinter as tk
from tkinter import filedialog
import re

# Function to parse the race results file
def parse_race_results(race_file):
    race_data = []
    with open(race_file, 'r') as f:
        lines = f.readlines()

    # Regex pattern to extract relevant data (Lap Time and Place)
    lap_pattern = r"(\d+)\s+(\S+)\s+([\d]+)'([\d]+)\"([\d]+)\s+(\d+)"
    
    for line in lines:
        match = re.match(lap_pattern, line.strip())
        if match:
            lane, bib, min_part, sec_part, hundredths, place = match.groups()

            # Skip lines where Bib is '----' or invalid
            if bib == "----":
                continue

            lap_time = f"{min_part}:{sec_part}.{hundredths}"
            race_data.append((lane, bib, lap_time, place))

    return race_data

# Function to parse the bib file
def parse_bib_file(bib_file):
    bib_numbers = []
    with open(bib_file, 'r') as f:
        lines = f.readlines()
    
    # Read all Bib numbers (skip first line "Bib")
    for line in lines[1:]:
        bib_numbers.append(line.strip())
    
    return bib_numbers

# Function to generate the .lif file
def generate_lif_file(merged_data, output_file):
    with open(output_file, 'w') as f:
        # Write the header of the .lif file
        f.write("Position,Bib,Lane,Last Name,First Name,Team,Time,License,Delta Time,Reac Time,Splits,Time Trial Start Time,User 1,User 2,User 3\n")
        
        # Write each race result entry
        for entry in merged_data:
            position, bib, lane, lap_time = entry
            # Placeholder names
            last_name = "Doe"
            first_name = "John"
            team = "Unknown"
            f.write(f"{position},{bib},{lane},{last_name},{first_name},{team},{lap_time},,,,,,,,\n")
    
    print(f"Merged data successfully written to {output_file}")

# Function to merge race results with bib numbers
def merge_race_and_bib(race_data, bib_numbers):
    merged_data = []
    position = 1

    # Create a dictionary of race results keyed by Bib
    race_dict = {entry[1]: entry for entry in race_data}

    # Match Bib numbers with race data
    for bib in bib_numbers:
        if bib in race_dict:
            lane, bib, lap_time, place = race_dict[bib]
            merged_data.append((position, bib, lane, lap_time))
            position += 1

    return merged_data

# Function to handle file selection and processing
def on_file_select():
    # Ask user to select the race results file
    race_file = filedialog.askopenfilename(title="Select Race Results File", filetypes=[("Text files", "*.txt")])
    if not race_file:
        return
    
    # Ask user to select the Bib numbers file
    bib_file = filedialog.askopenfilename(title="Select Bib Numbers File", filetypes=[("Text files", "*.txt")])
    if not bib_file:
        return
    
    # Parse the selected files
    race_data = parse_race_results(race_file)
    bib_numbers = parse_bib_file(bib_file)

    # Merge the data
    merged_data = merge_race_and_bib(race_data, bib_numbers)

    # Ask user to select output location for the .lif file
    output_file = filedialog.asksaveasfilename(title="Save Merged .lif File", defaultextension=".lif", filetypes=[("LIF files", "*.lif")])
    if output_file:
        generate_lif_file(merged_data, output_file)

# Set up the GUI
root = tk.Tk()
root.title("Race Results Merger")

# Set up the UI components
button = tk.Button(root, text="Select Files and Merge", command=on_file_select)
button.pack(pady=20)

# Start the GUI main loop
root.mainloop()
