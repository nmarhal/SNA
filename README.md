# Edge ideas
### directed
- x speaks before y
  - when x has a line before y, breaks when character is null (description text)
  - gives a rough model of x speaks to y, but this is not perfect
- x mentions y
  - when x mentions y in their line
### undirected
- x and y have lines in the same episode
- x and y have lines in the same book

# Cleanup
made a list of characters based on the character names in the first column of the script and based on list of aliases I 
found online and from chatGPT. I removed any character that does not have 
a page on https://avatar.fandom.com. then used this website to fill in 
the gender, their bending type and their origin. I then used these "approved" characters
to clean up my other datasets. The functions used to compute x mentions y and x speaks to y can be seen in
create_datasets.py. 

# visualization
I made visualize_graphs.py to get some first visuals on this data. You can see
how to use the function in main.py