# Lakeshore224 to MIDAS

Goal: connect to the Lakeshore224 temperature controller via ethernet and read the result to the MIDAS history. The direct application for this is for 
the source gradient measurement. 

## Resources

* [Lakeshore device model](https://www.lakeshore.com/products/categories/overview/temperature-products/cryogenic-temperature-monitors/model-224-temperature-monitor)
* See manual [here](https://www.lakeshore.com/docs/default-source/product-downloads/224_manual.pdf?sfvrsn=57de6414_7)
  * Section 6.4.1 details the ethernet configuration

## TCP Connection

* The port number used for TCP socket connections on the Model 224 is 7777.
* A maximum of two simultaneous socket connections can be made to the Model 224. Any attempts to open a new socket while two socket connections are already open on a Model 224 will fail.
* Two or more command strings or queries can be chained together in one communication, but they must be separated by a semi-colon (;). The total communication string must not exceed 255 characters in length.
* The instrument will respond only to the last query it receives. 
* A special ASCII character, line feed (LF 0AH), is used to indicate the end of a mes-age string. This is called the message terminator. The Model 224 will accept either the line feed character alone, or a carriage return (CR 0DH) followed by a line feed as the message terminator. The instrument query response terminator will include both carriage return and line feed.