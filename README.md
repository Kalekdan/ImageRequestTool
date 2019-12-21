# ImageRequestTool

Run imgRequestApp.py using the command ```python imgRequestApp.py```
This will start the python server at ```http://localhost:5000/```

To interact with the custom image request API, use the URL ```http://127.0.0.1:5000/get-custom-image?``` and specify the arguments as follows:


| Key        | Example Value                         | Description                                                                                                                                     |
|------------|---------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| img        | 02_04_2019_001158_2019-04-02-11-56-36 | The file name (without extension) of the image you want to request.<br>*Request will fail if not specified*                                           |
| res        | 1920x1080                             | The horizontal and vertical resolution with an 'x' as a separater of the output desired.<br>*Will retain original resolution if value not specified* |
| background | FF1E1A                                | The background color to set on the image given as a hex code.<br>*Will retain transparency if value not specified*                                   |
| watermark  | This is a watermark                   | Adds a watermark to the image returned using the string provided.<br>*Will not add a watermark if value not specified*                                |
| type       | gif                                   | The extension of the image type you would like returned.<br>*Returns image as '.png' if value not specified*                                          |
