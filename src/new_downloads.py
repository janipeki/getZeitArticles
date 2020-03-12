

class NewURLs: 
     def __init__(self): 
          self._url = []
       
     # using property decorator 
     # a getter function 
     @property
     def url(self): 
         print("Returning all URLs: " + str(self._url)) 
         return self._url 
       
     # a setter function 
     @url.setter 
     def url(self, newURL): 
         if(newURL == ""): 
            raise ValueError("URL may not be empty") 
         print("New URL: " + newURL)
         self._url.append(newURL)
