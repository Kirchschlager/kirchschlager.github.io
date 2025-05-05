import ads
import matplotlib.pyplot as plt
import numpy as np
print()
print("Please include your personalized API key. More details: \033[91m https://ui.adsabs.harvard.edu/help/api/\033[0m")
print()

# Set up your API key
API_KEY = "77RnJf024TS5cnt0TD8wJ0LofpollRVoIYjtVtBk"   
ads.config.token = API_KEY

nauthor = 1000

Startyear = 2011
Finalyear = 2025
Thresh_pub = 15

# Step 1: Query for 2015 PhD theses with pagination
# Ask the user if they want to include 'dust' in the abstract filter
include_dust = input("Do you want to include 'dust' in the abstract filter? (yes/no): ").strip().lower()
if include_dust == "yes":
    query_string = "doctype:phdthesis year:2015 property:refereed abs:'dust'"
    print("-> Create the list of authors with PhD in 2015 and with the word 'dust' in title or abstract of the thesis, in the order of the first-author publications.")
else:
    query_string = "doctype:phdthesis year:2015 property:refereed"
    print("-> Create the list of authors with PhD in 2015 in the order of the first-author publications.")

# Step 1: Query for 2015 PhD theses with pagination
thesis_query = ads.SearchQuery(q=query_string, fl=["author", "orcid"], rows=nauthor)
#thesis_query = ads.SearchQuery(q="doctype:phdthesis year:2015  property:refereed", fl=["author"], rows=nauthor)

# Set to hold unique author names
authors = set()

# Initialize pagination variables
start = 0
rows = nauthor  # Number of results per page

# Iterate through pages of search results and add authors to the set
while True:
    # Modify the start index to get the next page of results
    thesis_query.start = start
    
    # Perform the search and directly iterate over results
    results_found = False
    for paper in thesis_query:
        results_found = True  # We found results in this page
        if hasattr(paper, 'author') and paper.author:
            authors.update(paper.author)  # Add all authors to the set
    
    # If no results were found, we have reached the end of the available pages
    if not results_found:
        break
    
    # Move to the next page (next set of results)
    start += rows

# Limit the number of authors to 100 for better readability and performance
authors = list(authors)[:nauthor]

print()
print(f"Total authors to plot: {len(authors)}")  # Debugging print

# Step 2: Check publication counts for each author
author_publications = {}

#=====================================
# Search for all first-author publications by Kirchschlager, Florian
author_name2 = "Kirchschlager, Florian"
pub_query2 = ads.SearchQuery(q=f'first_author:"Kirchschlager, Florian" property:refereed (bibstem:"ApJ*" OR bibstem:"MNRAS" OR bibstem:"A&A*" OR bibstem:"AJ*" OR bibstem:"ApJL" OR bibstem:"SCI" OR bibstem:"NatCo" OR bibstem:"Nat" OR bibstem:"ApPhL")', fl=["year"])

# Create a dictionary to store the accumulated publications
accumulated_publications2 = 0

# Loop through the publications and accumulate them
for pub2 in pub_query2:
    if int(pub2.year) <= 2025:  # Accumulate until 2024
        accumulated_publications2 += 1

# Print the accumulated number of first-author publications by Kirchschlager, Florian
print()
print(f"Accumulated number of first-author publications by {author_name2} up to 2025: {accumulated_publications2}")
print()

#=====================================

# For each author, get their publications and calculate accumulated counts
ifk = 0
author_stats = []
author_publications = {}

# Convert all authors to "Last, First*" format using only the first given name
formatted_authors = []
for author in authors:
    parts = author.split(',')
    if len(parts) == 2:
        last = parts[0].strip()
        first_full = parts[1].strip()
        first_word = first_full.split()[0] if first_full else ''
        formatted = f"{last}, {first_word}"
    else:
        formatted = author  # fallback
    formatted_authors.append(formatted)

# Use formatted names in query and output
for author in formatted_authors:  # Take this line if you want to query only the first letter(s) of the first name
#for author in authors:           # Take this line if you want to query the full first name
    pub_query = ads.SearchQuery(
        q=f'(first_author:"{author}" OR first_author:"{author}*") property:refereed (bibstem:"ApJ*" OR bibstem:"MNRAS" OR bibstem:"A&A*" OR bibstem:"AJ*" OR bibstem:"ApJL" OR bibstem:"SCI" OR bibstem:"NatCo" OR bibstem:"Nat" OR bibstem:"ApPhL")',
        fl=["year", "author"]
    )

    publication_counts = {}
    for pub in pub_query:
        year = int(pub.year)
        publication_counts[year] = publication_counts.get(year, 0) + 1

    accumulated_counts = []
    running_total = 0
    current_year = Startyear
    while current_year <= Finalyear:
        if current_year in publication_counts:
            running_total += publication_counts[current_year]
        accumulated_counts.append(running_total)
        current_year += 1

    ifk += 1
    author_stats.append((author, accumulated_counts[Finalyear - Startyear]))
    print(f' {ifk}/{len(authors)}')
    #print(ifk, author, ":", accumulated_counts[Finalyear - Startyear])

    author_publications[author] = (range(Startyear, Finalyear + 1), accumulated_counts)


print()
print("Sort the authors by the number of first-author publications (name ambiguity not considered):")
print("Name ambiguity has to be analysed by hand for each name separately.")
# Sort authors by final accumulated count and print
sorted_stats = sorted(author_stats, key=lambda x: x[1], reverse=True)
for idx, (author, count) in enumerate(sorted_stats, 1):
    print(idx, author,":", count)

# Export sorted stats to CSV
import csv
with open("author_publication_stats.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Rank", "Author", "Final Accumulated Count"])
    for idx, (author, count) in enumerate(sorted_stats, 1):
        writer.writerow([idx, author, count])
print()
print("Author statistics exported to 'author_publication_stats.csv' ✅")
print()
    #print()
    
# Step 3: Plot the accumulated data for each author
plt.figure(figsize=(12, 8))  # Larger figure for visibility

# Plot each author's data as a cross ('x') and shift points slightly for overlapping data
for author, (years, accumulated_counts) in author_publications.items():
    # Add a small random offset to both the x and y coordinates to avoid overlapping points
    x_offsets = np.random.uniform(-0.1, 0.1, len(years))  # Small random shift in x
    y_offsets = np.random.uniform(-0.1, 0.1, len(years))  # Small random shift in y
    if "Kirchschlager, Florian" in author or "Kirchschlager, F" in author:
        plt.scatter(np.array(years) + x_offsets, np.array(accumulated_counts) + y_offsets,
                    color='red', marker='x', alpha=0.9, s=60, linewidths=2.5,  zorder=10, # Higher zorder = front
                    label="Kirchschlager, Florian")
    else:
        plt.scatter(np.array(years) + x_offsets, np.array(accumulated_counts) + y_offsets,# Lower zorder = background
            zorder=1, color='b', marker='x', alpha=0.7, s=40)
    
    #plt.scatter(np.array(years) + x_offsets, accumulated_counts + y_offsets, color='b', marker='x', alpha=0.7, edgecolors='w', s=40)
    #plt.scatter(np.array(years) + x_offsets, accumulated_counts + y_offsets, color='b', marker='x', alpha=0.7, edgecolors='w', s=40)
# Set x-range from 2009.5 to 2025.5
plt.xlim(Startyear-0.5, Finalyear + 0.5)



# Set x-ticks for every second year
plt.xticks(range(Startyear+1, Finalyear+1, 2), fontsize=14)

# Set labels and title with larger font size (adjusted title size)
plt.xlabel("Year", fontsize=18)
plt.ylabel("Accumulated First-Author Publications", fontsize=18)
plt.title("Accumulated First-Author Publications Over Time for Each Author (2015 PhDs)", fontsize=14)  # Reduced by 30%
plt.grid(True)

# Step 4: Calculate and print the percentage of authors with more than 15 accumulated publications in 2024
authors_above_16_2025 = sum([1 for counts in author_publications.values() if counts[1][Finalyear-Startyear] > Thresh_pub])  # Check publications accumulated by 2025 (index 15)
total_authors = len(authors)
percentage_above_16_2025 = (authors_above_16_2025 / total_authors) * 100

print(f"Percentage of authors with more than {Thresh_pub} accumulated first-author publications in {Finalyear}: {percentage_above_16_2025:.2f}%")

# Add the percentage text below the xlabel
plt.figtext(0.1, -0.01, f"Number of authors: {len(authors)}", ha="left", fontsize=14)
plt.figtext(0.1, -0.05, f"Percentage of authors with more than {Thresh_pub} accumulated first-author publications in {Finalyear}: {percentage_above_16_2025:.2f}%", ha="left", fontsize=14)

#add a legend just below this block:
plt.legend(fontsize=14)

# Set y-ticks font size
plt.yticks(fontsize=14)
plt.yticks(ticks=np.arange(0, 30, 2), fontsize=14)
#plt.ylim(-1, 24)

# Increase the bottom border to make room for the text
plt.subplots_adjust(bottom=0.1)  # Adjusting margin at the bottom to fit the text

# Save the plot as PDF with larger border widths (1cm each side)
plt.tight_layout()  # Adjust layout to avoid clipping
plt.savefig("accumulated_publications_2015_phds_2024_percentage.pdf", bbox_inches='tight', pad_inches=0.75)

# Display the plot
plt.show()
