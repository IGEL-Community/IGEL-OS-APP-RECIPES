THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Download IntelliJ IDEA - Linux x86_64 (tar.gz)

https://www.jetbrains.com/idea/download/other.html

- Note the version of the file
- Rename file to `idea.tar.gz`

-----

## Installation Instructions

```
IntelliJ IDEA

INSTALLATION INSTRUCTIONS
===============================================================================

  1. Unpack the IntelliJ IDEA distribution archive that you downloaded
     where you wish to install the program. We will refer to this
     location as your {installation home}.

  2. To start the application, open a console, cd into "{installation home}/bin" and type:

       ./idea.sh

     This will initialize various configuration files in the configuration directory:
     ~/.config/JetBrains/Idea__version__

  3. [OPTIONAL] Add "{installation home}/bin" to your PATH environment
     variable so that you can start IntelliJ IDEA from any directory.

  4. [OPTIONAL] To adjust the value of the JVM heap size, create a file idea.vmoptions
     (or idea64.vmoptions if using a 64-bit JDK) in the configuration directory
     and set the -Xms and -Xmx parameters. To see how to do this,
     you can reference the vmoptions file under "{installation home}/bin" as a model
     but do not modify it, add your options to the new file.

  [OPTIONAL] Change the location of the "config" and "system" directories
  ------------------------------------------------------------------------------

  By default, IntelliJ IDEA stores all your settings in the
  ~/.config/JetBrains/Idea__version__ directory
  and uses ~/.local/share/JetBrains/Idea__version__ as a data cache.
  To change the location of these directories:

  1. Open a console and cd into ~/.config/JetBrains/Idea__version__

  2. Create a file idea.properties and set the idea.system.path and idea.config.path variables, for example:

     idea.system.path=~/custom/system
     idea.config.path=~/custom/config

  NOTE: Store the data cache ("system" directory) on a disk with at least 1 GB of free space.
  ```

-----

## Git Configuration

[Customizing Git - Git Configuration](https://git-scm.com/book/en/v2/Customizing-Git-Git-Configuration)

```bash
$ git config --global user.name "John-Doe"
$ git config --global user.email johndoe@example.com
  ```

This is written into `~/.gitconfig` and the content of the file looks like this:

```bash
[user]
	name = John-Doe
	email = johndoe@example.com
  ```
