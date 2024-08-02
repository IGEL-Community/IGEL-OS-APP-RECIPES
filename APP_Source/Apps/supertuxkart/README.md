THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Building the app SuperTuxKart

![SuperTuxKart](data/app.png)

This document describes how to build an app from the sources. If you want to build an app yourself from scratch follow the example in [Creating](Creating.md)

## Table of Contents
1. [Installing prerequisites](#prerequisites)
2. [Building](#building)
3. [Configuring signing](#configuring-signing)
4. [Signing](#signing)
5. [Installing](#installing)


## Prerequisites

We currently support Ubuntu 18.04 and newer. Install igelpkg as described in the document "Getting Started With the IGEL OS App SDK-v7.pdf" of the SDK.

## Building

Clone and build the app.
```bash
git clone https://github.com/IGELTechnologyGmbH/supertuxkart.git
cd supertuxkart
igelpkg build -r bookworm -sp
```
The app is now signed and ready to install

## Installing

Copy the file igelpkg.output/supertuxkart-1.4.0.ipkg to an usb drive and install it.
```bash
igelpkgctl install -f /media/supertuxkart-1.4.0.ipkg
```
