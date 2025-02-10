Template for a Smartcard middleware


The variables in igel/variables.json must be adopted to the middleware

    "name": "pkcs11_template",
    "summary": "pkcs11_template smartcard framework",
    "version": "1.0.0",

e.g.

The archive_url is the location of the archive containing the shared library. file:// and http:// are supported:

    "archive_url": "file:///mnt/files/software/libcryptoki.so.4.2.zip",

libpath must be set to the path of the shared library on the target system:

    "libpath": "/services/pkcs11_template/libcryptoki.so.4.2"


The fields "author" and "vendor" must be filled in app.json for the app to be built successfully.

You can update the metadata and the icons that will be displayed in the UMS.

data/descriptions/en Contains the short and long description of the app

data/app.svg Is the app icon

data/monochrome.svg Is the monochrome version of app icon

-----

PKCS#11 is a cryptographic token interface standard, which specifies an API, called Cryptoki.

PKCS#11 was developed by the RSA Labs but is now an open standard managed by the OASIS PKCS 11 Technical Committee.

https://www.oasis-open.org/committees/pkcs11/
