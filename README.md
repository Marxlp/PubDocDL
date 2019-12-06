# PubDocDL
*PubDocDL*(Public Documents Downloader) is a project to make the downloading some publicly accessible documents more easily.

## Brief Description

### Public Requirements
The *python3.x* is needed. Besides all the third party libraries required in each downloader have been listed in `requirements.txt` files in their own folders.
### 1. book118 (target: book118.com)
#### Usage:
`python book118/book118downloader.py [-d DELAY] url_link`
#### Example:
`python book118/book118downloader.py https://max.book118.com/html/2018/0928/6012032034001221.shtm`

or delay for 10s before downloading, if the network condition is bad

`python book118/book118downloader.py -d 10 https://max.book118.com/html/2018/0928/6012032034001221.shtm`
#### Special Requirements:
*fpdf*, *selenium*, *chrome webdriver*
#### Limitation:
current only support *pdf, docx, doc*

## License
GNU GPL v3.0
