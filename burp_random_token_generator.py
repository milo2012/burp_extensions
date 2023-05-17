from burp import IBurpExtender, IProxyListener, ITab, IHttpListener, IExtensionStateListener, IContextMenuFactory, ISessionHandlingAction
from java.io import PrintWriter
from java.net import Proxy, InetSocketAddress
from javax.swing import JPanel, JLabel, JTextArea, JTextField, BoxLayout
from java.awt import BorderLayout
from javax.swing.BoxLayout import Y_AXIS
import re
import random	

'''
This is similar to https://github.com/portswigger/token-incrementor.
Token Incrementor adds the Incremented text to every new token which might affect the testing.
Burp Extension in Python makes it easier to modify.
That's the purpose of this script.
'''


class BurpExtender(IBurpExtender, ITab, IProxyListener, IHttpListener, IExtensionStateListener, IContextMenuFactory, ISessionHandlingAction):

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("RandNum Replacer")

        # Create an instance of the Tab class
        self.tab = self.Tab(self)
                
        self.keywordField = None  # Instance variable for keywordField
        self.prefixField = None  # Instance variable for keywordField
        self.startingNumberField = None  # Instance variable for keywordField
        self.endingNumberField = None  # Instance variable for keywordField
        
        # Add a new tab called "IntMePlease" to Burp Suite
        callbacks.addSuiteTab(self.tab)

        self.stdout = PrintWriter(callbacks.getStdout(), True)
        self.stderr = PrintWriter(callbacks.getStderr(), True)

        callbacks.registerProxyListener(self)
        callbacks.registerHttpListener(self)
        callbacks.registerExtensionStateListener(self)
        callbacks.registerContextMenuFactory(self)
        callbacks.registerSessionHandlingAction(self)

    class Tab(ITab):
        def __init__(self, extender):
            self._extender = extender
            self.keywordField = None  # Instance variable for keywordField
            self.endingNumberField = None  # Instance variable for keywordField
            self.keywordField = None  # Instance variable for keywordField

        def getTabCaption(self):
            return "RandNum_Replacer"
            
        def getUiComponent(self):
            panel = JPanel(BorderLayout())

            label = JLabel("RandNum Replacer")
            panel.add(label, BorderLayout.NORTH)

            innerPanel = JPanel()
            innerPanel.setLayout(BoxLayout(innerPanel, Y_AXIS))

            self.keywordLabel = JLabel("Keyword (Replace):")
            self.keywordField = JTextField("IntMePlease", 10)
            self.keywordField.setMaximumSize(self.keywordField.getPreferredSize())

            self.prefixLabel = JLabel("Prefix (Optional):")
            self.prefixField = JTextField(10)
            self.prefixField.setMaximumSize(self.prefixField.getPreferredSize())

            self.startingNumberLabel = JLabel("Starting Number:")
            self.startingNumberField = JTextField("100000", 10)
            self.startingNumberField.setMaximumSize(self.startingNumberField.getPreferredSize())

            self.endingNumberLabel = JLabel("Ending Number:")
            self.endingNumberField = JTextField("999999", 10)
            self.endingNumberField.setMaximumSize(self.endingNumberField.getPreferredSize())
            
            # Set the horizontal alignment of the labels to left
            self.keywordLabel.setHorizontalAlignment(JLabel.LEFT)
            self.prefixLabel.setHorizontalAlignment(JLabel.LEFT)
            self.startingNumberLabel.setHorizontalAlignment(JLabel.LEFT)
            self.endingNumberLabel.setHorizontalAlignment(JLabel.LEFT)
            
            innerPanel.add(self.keywordLabel)
            innerPanel.add(self.keywordField)
            innerPanel.add(self.prefixLabel)
            innerPanel.add(self.prefixField)
            innerPanel.add(self.startingNumberLabel)
            innerPanel.add(self.startingNumberField)
            innerPanel.add(self.endingNumberLabel)
            innerPanel.add(self.endingNumberField)
            panel.add(innerPanel, BorderLayout.CENTER)
            return panel
             
    def createTab(self):
        # Create a new panel to hold the UI components for the "IntMePlease" tab
        panel = JPanel(BorderLayout())

        # Add the UI components to the panel
        panel.add(JLabel("RandNum Replacer"), BorderLayout.NORTH)
        panel.add(JTextArea("This is the RandNum tab."), BorderLayout.CENTER)

        return panel
        
    def extensionUnloaded(self):
        # Perform cleanup tasks here if needed
        pass

    def processProxyMessage(self, messageIsRequest, message):
        pass

    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        if not self._callbacks.isInScope(messageInfo.getUrl()):
            return None

        tool_name = self.getToolName(toolFlag)
        url = str(messageInfo.getUrl())
        self.stdout.println("URL: {}".format(url))
        keyword = self.tab.keywordField.getText()
        prefix = self.tab.prefixField.getText()
        startingNumber = int(self.tab.startingNumberField.getText())
        endingNumber = int(self.tab.endingNumberField.getText())
        
        if messageIsRequest and (toolFlag == self._callbacks.TOOL_PROXY or toolFlag == self._callbacks.TOOL_INTRUDER or toolFlag == self._callbacks.TOOL_REPEATER or toolFlag == self._callbacks.TOOL_TARGET) and keyword in url:
			# Get the HTTP request message
			if "Modified" in messageInfo.getComment():
				self.stdout.println("Modified")
				return None
			http_request = messageInfo.getRequest()
			# Convert the request body to a string
			request_str = self._helpers.bytesToString(http_request)
			# Replace "IntMePlease" with a random 6-digit number
						
			http_request = messageInfo.getRequest()
			request_str = self._helpers.bytesToString(http_request)
			rand_num = str(random.randint(startingNumber, endingNumber))
			#request_str = re.sub(keyword, rand_num, request_str)
			request_str = re.sub(keyword, self.tab.prefixField.getText() + rand_num, request_str)

			self.stdout.println("\nRandom number {}:".format(request_str))
                        			
			# Convert the modified request body back to bytes
			new_request = self._helpers.stringToBytes(request_str)
			# Print the modified request with tool information
			modified_request = self._helpers.bytesToString(new_request)
			self.stdout.println("\nModified Request from {}:".format(tool_name))
			self.stdout.println(modified_request)
			# Update the message with the modified request
			messageInfo.setRequest(new_request)
			messageInfo.setComment("Modified")
        # Return None since the message is modified in place
        return None

    def getActionName(self):
        return "RandNum Replacer"

    def getToolName(self, toolFlag):
        if toolFlag == self._callbacks.TOOL_PROXY:
            return "PROXY"
        elif toolFlag == self._callbacks.TOOL_REPEATER:
            return "REPEATER"
        elif toolFlag == self._callbacks.TOOL_TARGET:
            return "TARGET"
        else:
        	return "UNKNOWN"

	def createMenuItems(self, invocation):
		# Return None since we don't need to add context menu items
		return None		



		