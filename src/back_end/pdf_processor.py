'''

The Why: We want to convert the pdf to image for processing allowing su to choose a grey scaleand control imahgge format for best optimization of the image processing in the other file


Given: PDF file from front end 
outcome: image file to be used in image processing in other file 


Libraries to use:
- pdf2image

'''
from pdf2image import convert_from_path
'''
wait on uploading files from front end and then process the file to convert it to image'''

images = convert_from_path(
    "input.pdf",
    dpi=300,
    fmt="png",
    grayscale=True,
    output_folder="pages",
    output_file="page",
    thread_count=4
)


