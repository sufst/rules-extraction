import pdftotext

# Load PDF
with open("rules.pdf", "rb") as f:
    pdf = pdftotext.PDF(f)

# Test print of first page
print(pdf[0])

# To print all pages uncomment below

# for page in pdf:
#    print(page)
