THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [Selenium Web Browser Automation - Java](https://www.selenium.dev/downloads/)

- Download latest Java package
- Rename to `selenium-java.zip`

**NOTE:** Requires the following app be created and setup in UMS - [Azul Zulu OpenJDK](https://github.com/IGEL-Community/IGEL-OS-APP-RECIPES/tree/main/APP_Source/Apps/azul_openjdk)

-----

# Java Path

```bash linenums="1"
pushd .
cd /services/azul_openjdk/zulu*
eval JAVA_HOME=$(pwd)
PATH=$JAVA_HOME/bin:$PATH
popd
```

-----

# Simple Selenium Test (EdgeTest.java)

- Create file called `EdgeTest.java`

```java linenums="1"
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.edge.EdgeDriver;

public class EdgeTest {
    public static void main(String[] args) {
        // Optional: set the path to msedgedriver manually if not in PATH
        // System.setProperty("webdriver.edge.driver", "C:\\path\\to\\msedgedriver.exe");

        // 1. Launch Edge browser
        WebDriver driver = new EdgeDriver();

        // 2. Open a test website
        driver.get("https://igel-community.github.io/IGEL-Docs-v02/");

        // 3. Print and verify the title
        String title = driver.getTitle();
        System.out.println("Page title is: " + title);

        if (title.contains("IGEL Community Docs")) {
            System.out.println("✅ Test Passed!");
        } else {
            System.out.println("❌ Test Failed!");
        }

        // 4. Close the browser
        driver.quit();
    }
}
```

- Compile `EdgeTest.java`

```bash linenums="1"
javac -cp ".:/services/selenium/*" EdgeTest.java
```

- Run `EdgeTest`

```bash linenums="1"
java -cp ".:/services/selenium/*" EdgeTest
```