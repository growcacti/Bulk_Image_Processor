# Bulk_Image_Processor
mergek, split with thumbnail view
Features are 
Recursive Directory Browsing: Now, the application can recursively list images from selected directories.
Image Information Display: As users select an image from the list, it will display the file's path, size, and last modification date.
Combined Merging Functionality: The user can select multiple images from the list to merge them.
Recursive Image Browsing: Uses glob to retrieve images recursively.
Image Info Display: Shows file path, size, and modification date for selected images.
Merging Images: Combines the selected images into a single merged image.
Combined GUI: Integrates browsing, viewing, and merging functionality into one application.
Recursive/Flat View Toggle: Users can choose to view images in the selected directory either recursively or non-recursively.
Thumbnails with Info: Thumbnails are displayed along with the image name, size, and path.
new version includes:
Added a 'Unselect' button: Allows users to remove files from the selection list.
Added a listbox to display selected files: Shows the names of selected files.
Added an info section: Displays more detailed information (e.g., path, size, and last modified date) about the currently highlighted image.
Changed selection to double-click: Users now need to double-click to add an image to the selection.
Save absolute paths when bookmarking.
Add a bookmark loading option to handle reloading images from saved bookmarks.
Bookmark Save/Load:

    Added methods to save bookmarks with absolute image paths.
    Bookmarks are stored in a JSON file.

Path Handling:

    Absolute paths are saved and reloaded to prevent path errors.

Reloading:

    Ensures images are displayed correctly after loading a bookmark.



Key Fixes:

    The update_view method was incorrectly referred to in the Checkbutton callback before being defined.
    The image_paths attribute was referenced before being properly defined.




updated:

    Threading for Image Loading: Added threading for the load_images function to prevent GUI freezing.
'Exit' Button: Allows users to exit the program gracefully.
'Clear Thumbnails' Button: Clears all displayed thumbnails from the canvas.
