import csv
from tkinter import Tk, filedialog

def nk2000xc_to_lif():
    """
    Converts NK2000XC export file content into a LIF file format.
    Opens a dialog box to select the NK2000XC input file.
    """
    # Open file dialog to select the input file
    Tk().withdraw()  # Hide the root Tkinter window
    nk2000xc_file = filedialog.askopenfilename(
        title="Select NK2000XC Export File",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )

    if not nk2000xc_file:
        print("No file selected. Exiting.")
        return

    # Ask for output file location
    lif_file = filedialog.asksaveasfilename(
        title="Save LIF File As",
        defaultextension=".lif",
        filetypes=[("LIF Files", "*.lif"), ("All Files", "*.*")]
    )

    if not lif_file:
        print("No output file selected. Exiting.")
        return

    # Read the NK2000XC file
    nk_data = []
    with open(nk2000xc_file, 'r') as infile:
        reader = csv.DictReader(infile, delimiter='\t')  # Assuming tab-delimited
        for row in reader:
            nk_data.append(row)

    # Prepare the LIF data structure
    lif_data = []

    # Iterate over NK2000XC data and convert
    position = 1  # Start with position 1
    for row in nk_data:
        # Extract time from the NK2000XC row if available
        time = row.get("Cum Time", "")  # Adjust the key if necessary

        # Create a LIF entry with only the necessary fields populated
        lif_entry = {
            "Position": position,
            "Bib": f"10{position}",  # Assigning dummy Bib numbers for illustration
            "lane": "1",  # Default lane to 1, modify as needed
            "last name": "Competitor",
            "first name": f"{position}",
            "Team": "TeamName",  # Assign a placeholder team name
            "Time": time,  # Use the extracted time value
            "license": "",
            "delta time": "",
            "ReacTime": "",
            "splits": "",
            "time trial start time": "",
            "user 1": "",
            "user 2": "",
            "user 3": "",
        }
        lif_data.append(lif_entry)
        position += 1

    # Write the LIF file
    fieldnames = [
        "Position", "Bib", "lane", "last name", "first name", "Team",
        "Time", "license", "delta time", "ReacTime", "splits",
        "time trial start time", "user 1", "user 2", "user 3"
    ]

    with open(lif_file, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(lif_data)

    print(f"Converted {nk2000xc_file} to {lif_file}.")

# Example usage
if __name__ == "__main__":
    nk2000xc_to_lif()
