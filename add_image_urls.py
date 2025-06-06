import csv

input_file = 'poke-num.csv'
output_file = 'poke-num-with-images.csv'

with open(input_file, newline='', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ['image_url']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        dex_number = row['dex_number'].strip()
        row['image_url'] = f'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{dex_number}.png'
        writer.writerow(row)

print(f"✅ Saved enhanced file to: {output_file}")
