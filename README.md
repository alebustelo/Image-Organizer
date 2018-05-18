# Image-Organizer
An image organizing tool

This application will list all the images in a directory. The user can designate up to four destination directories, each mapped to one quadrant and a corresponding color. For example, the top left of an image corresponds to the color blue. Clicking on an image's top left quadrant creates a blue box behind the image that marks that images as selected, and when the execute button is clicked, all images marked with blue boxes will be moved to the folder specified in the blue directory button. Images can be marked for more than one color/directory at the same time so an image can be copied to all the marked directories, and then the original deleted.

The problem I am trying to solve with this application is having hundreds or thousands of images in a single directory and having to sort them into sub-directories. Doing this by hand using ctrl+right-click or shift+right-click or even ctrl+shift+right-click is tedius, error-prone, and one accidental misclick can undo hundreds of selections. Once this application is done, this particular type of task should be much easier and much less frustrating.

The PIL package is required to run the program. These should work.
On Windows:
pip3 install Pillow

On Ubuntu:
sudo apt install python3-pil
sudo apt install python3-pil.imagetk

I am building it in Python 3 as a way to practice building a tkinter GUI and to try to build something that I sort of want for myself. First step is to get it working, but I'll be cleaning it up after I'm done.

There is currently a bug when loading a lot of images at once where the image library reports a memory error. I read online it might be a bug in the library, but it could also be something I did. Still working on this.

There are numerous other bugs that I am aware of but I'm working on those too.

I shouldn't have to say this, but this program is very, VERY buggy and could potentially delete stuff you don't want it to or cause other unspecified damage. I mean, it shouldn't, but you never know. Use at your own risk.

I added a license because I don't want any trouble, but there's not much to see right now.
