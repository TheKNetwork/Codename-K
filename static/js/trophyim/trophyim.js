/*
    This program is distributed under the terms of the MIT license.
    Please see the LICENSE file for details.

    Copyright 2008 Michael Garvin
*/
/*TODO dump / very loose roadmap
--0.4
add chats to json store
Mouseover status messages in roster
HTML in messages (xslt?)
Select presence status/message
Optional user-specified resource
Loglevel select on login instead of check box
vcard support http://xmpp.org/extensions/xep-0153.html
Notifications of closed chats
Notifications of typing
--0.5
roster management
figure out how we want to handle presence from our own jid (and transports)
roster sorting by presence / offline roster capablility
auto-subscribe vs prompted subscribe based on config option
make sure makeChat() et al. can handle empty resources
    (offline chat capabilities)
--1.0 (or whenever someone submits better .css)
layout overhaul
code cleanup (like checking for excessive function lengths)
roster versioning http://xmpp.org/extensions/attic/xep-0237-0.1.html
make sure onload bootstrapping actually preserves existing onloads
*/
var TROPHYIM_BOSH_SERVICE = 'http://staging.theknetwork.org/http-bind/';  //Change to suit
var TROPHYIM_LOG_LINES = 200;
var TROPHYIM_LOGLEVEL = 1; //0=debug, 1=info, 2=warn, 3=error, 4=fatal
var TROPHYIM_VERSION = "0.3";
//Uncomment to make session reattachment work
//var TROPHYIM_JSON_STORE = "json_store.php";

/** File: trophyimclient.js
 *  A JavaScript front-end for strophe.js
 *
 *  This is a JavaScript library that runs on top of strophe.js.  All that
 *  is required is that your page have a <div> element with an id of
 *  'trophyimclient', and that your page does not explicitly set an onload
 *  event in its <body> tag.  In that case you need to append TrophyIM.load()
 *  to it.
 *
 *  The style of the client can be conrolled via trophyim.css, which is
 *  auto-included by the client.
 */

/** Object: HTMLSnippets
 *
 *  This is the repository for all the html snippets that TrophyIM uses
 *
 */
HTMLSnippets = {
    cssLink :
        "<link rel='stylesheet' href='trophyim.css' type='text/css'\
        media='screen' />",
    loginPage : "<div id='trophyimlogin'>\
        <form name='cred'><label for='trophyimjid'>JID:</label>\
        <input type='text' id='trophyimjid' /><br />\
        <label for='trophyimpass'>Password:</label>\
        <input type='password' id='trophyimpass' /><br />\
        <label for='trophyimloglevel'>Logging</label>\
        <input type='checkbox' id='trophyimloglevel' /><br />\
        <input type='button' id='trophyimconnect' value='connect'\
        onclick='TrophyIM.login()'/></form></div>",
    loggingDiv : "<div id='trophyimlog' />",
    rosterDiv : "<div id='trophyimroster' />",
    rosterGroup : "<div class='trophyimrostergroup'>\
        <div class='trophyimrosterlabel' /></div>",
    rosterItem : "<div class='trophyimrosteritem'\
        onclick='TrophyIM.rosterClick(this)'><div class='trophyimrosterjid' />\
        <div class='trophyimrostername' /></div>",
    statusDiv : "<div id='trophyimstatus'><span>Status:</span>\
        <span id='trophyimstatuslist'>Select box</span><br /><form>\
        <input type='button' value='disconnect' onclick='TrophyIM.logout()'/>\
        </form></div>",
    chatArea : "<div id='trophyimchat'><div id='trophyimchattabs' /></div>",
    chatBox : "<div><div class='trophyimchatbox' />\
        <form name='chat' onsubmit='TrophyIM.sendMessage(this); return(false);'>\
        <textarea class='trophyimchatinput' rows='3' cols='50'></textarea>\
        <input type='button' value='Send' onclick='TrophyIM.sendMessage(this)' />\
        </form></div>",
    chatTab :
        "<div class='trophyimchattab' onclick='TrophyIM.tabClick(this);'>\
            <div class='trophyimchattabjid' /><div class='trophyimtabclose'\
            onclick='TrophyIM.tabClose(this);'>x</div>\
            <div class='trophyimchattabname' />\
        </div>"
};

/** Object: DOMObjects
 *  This class contains builders for all the DOM objects needed by TrophyIM
 */
DOMObjects = {
    /** Function: xmlParse
     *  Cross-browser alternative to using innerHTML
     *  Parses given string, returns valid DOM HTML object
     *
     *  Parameters:
     *    (String) xml - the xml string to parse
     */
    xmlParse : function(xmlString) {
        var xmlObj = this.xmlRender(xmlString);
        if(xmlObj) {
            try { //Firefox, Gecko, etc
                if (this.processor == undefined) {
                    this.processor = new XSLTProcessor();
                    this.processor.importStylesheet(this.xmlRender(
                    '<xsl:stylesheet version="1.0"\
                    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">\
                    <xsl:output method="html" indent="yes"/><xsl:template\
                    match="@*|node()"><xsl:copy><xsl:copy-of\
                    select="@*|node()"/></xsl:copy></xsl:template>\
                    </xsl:stylesheet>'));
                }
                var htmlObj =
                this.processor.transformToDocument(xmlObj).documentElement;
                //Safari has a quirk where it wraps dom elements in <html><body>
                if (htmlObj.tagName.toLowerCase() == 'html') {
                    htmlObj = htmlObj.firstChild.firstChild;
                }
                return document.importNode(htmlObj, true);
            } catch(e) {
                try { //IE is so very very special
                    var htmlObj = document.importNode(xmlObj.documentElement, true);
                    if (htmlObj.tagName.toLowerCase() == "div") {
                        var div_wrapper = document.createElement('div');
                        div_wrapper.appendChild(htmlObj);
                        if(div_wrapper.innerHTML) {
                            div_wrapper.innerHTML = div_wrapper.innerHTML;
                        }
                        htmlObj = div_wrapper.firstChild;
                    }
                    return htmlObj;
                } catch(e) {
                    alert(
                    "TrophyIM Error: Cannot add html to page" + e.message);
                }
            }
        }
    },
    /** Function: xmlRender
     *  Uses browser-specific methods to turn given string into xml object
     *
     *  Parameters:
     *    (String) xml - the xml string to parse
     */
    xmlRender : function(xmlString) {
        try {//IE
            var renderObj = new ActiveXObject("Microsoft.XMLDOM");
            renderObj.async="false";
            if(xmlString) {
                renderObj.loadXML(xmlString);
            }
        } catch (e) {
            try { //Firefox, Gecko, etc
                if (this.parser == undefined) {
                    this.parser = new DOMParser();
                }
                var renderObj = this.parser.parseFromString(xmlString,
                "application/xml");
            } catch(e) {
                alert("TrophyIM Error: Cannot create new html for page");
            }
        }

        return renderObj;
    },
    /** Function: getHTML
     *  Returns named HTML snippet as DOM object
     *
     *  Parameters:
     *    (String) name - name of HTML snippet to retrieve (see HTMLSnippets
     *    object)
     */
    getHTML : function(page) {
        return this.xmlParse(HTMLSnippets[page]);
    },
    /** Function: getScript
     *  Returns script object with src to given script
     *
     *  Parameters:
     *    (String) script - name of script to put in src attribute of script
     *    element
     */
    getScript : function(script) {
        var newscript = document.createElement('script');
        newscript.setAttribute('src', script);
        newscript.setAttribute('type', 'text/javascript');
        return newscript;
    }
};

/** Object: TrophyIM
 *
 *  This is the actual TrophyIM application.  It searches for the
 *  'trophyimclient' element and inserts itself into that.
 */
TrophyIM = {
    /** Constants:
     *
     *    (Boolean) stale_roster - roster is stale and needs to be rewritten.
     */
    constants : {stale_roster: false},
    /** Object: chatHistory
     *
     *  Stores chat history (last 10 message) and current presence of active
     *  chat tabs.  Indexed by jid.
     */
    chatHistory : {},
    /** Object: activeChats
     *
     *  This object stores the currently active chats.
     */
    activeChats : {current: null, divs: {}},
    /** Function: setCookie
     *
     *  Sets cookie name/value pair.  Date and path are auto-selected.
     *
     *  Parameters:
     *    (String) name - the name of the cookie variable
     *    (String) value - the value of the cookie variable
     */
    setCookie : function(name, value) {
        var expire = new Date();
        expire.setDate(expire.getDate() + 365);
        document.cookie = name + "=" + value + "; expires=" + expire.toGMTString();
    },
    /** Function: delCookie
     *
     *  Deletes cookie
     *
     *  Parameters:
     *    (String) name) - the name of the cookie to delete
     */
    delCookie : function(name) {
        var expire = new Date();
        expire.setDate(expire.getDate() - 365);
        document.cookie = name + "= ; expires=" + expire.toGMTString();
        delete TrophyIM.cookies[name];
    },
    /** Function: getCookies
     *
     *  Retrieves all trophyim cookies into an indexed object.  Inteneded to be
     *  called once, at which time the app refers to the returned object instead
     *  of re-parsing the cookie string every time.
     *
     *  Each cookie is also re-applied so as to refresh the expiry date.
     */
    getCookies : function() {
        var cObj = {};
        var cookies = document.cookie.split(';');
        for (var c in cookies) {
            while (cookies[c].charAt(0)==' ') { 
                cookies[c] = cookies[c].substring(1,cookies[c].length);
            }
            if (cookies[c].substr(0, 8) == "trophyim") {
                var nvpair = cookies[c].split("=", 2);
                cObj[nvpair[0]] = nvpair[1];
                TrophyIM.setCookie(nvpair[0], nvpair[1]);
            }
        }
        return cObj;
    },
    /** Function: load
     *
     *  This function searches for the trophyimclient div and loads the client
     *  into it.
     */
    load : function() {
        TrophyIM.cookies = TrophyIM.getCookies();
        var client_div = document.getElementById('trophyimclient');
        if (client_div) {
            TrophyIM.client_div = client_div;
            //load .css
            document.getElementsByTagName('head')[0].appendChild(
            DOMObjects.getHTML('cssLink'));
            //Load other .js scripts needed
            document.getElementsByTagName('head')[0].appendChild(
            DOMObjects.getScript('strophejs/strophe.js'));
            document.getElementsByTagName('head')[0].appendChild(
            DOMObjects.getScript('strophejs/md5.js'));
            document.getElementsByTagName('head')[0].appendChild(
            DOMObjects.getScript('strophejs/sha1.js'));
            document.getElementsByTagName('head')[0].appendChild(
            DOMObjects.getScript('strophejs/b64.js'));
            document.getElementsByTagName('head')[0].appendChild(
            DOMObjects.getScript('json2.js')); //Keep this script last
            //Wait a second to give scripts time to load
            setTimeout("TrophyIM.showLogin()", 500);
        } else {
            alert("Cannot load TrophyIM client.\nClient div not found.");
        }
    },
    /** Function: storeData
     *
     *  Store all our data in the JSONStore, if it is active
     */
    storeData : function() {
        if (TrophyIM.connection && TrophyIM.connection.connected) {
            TrophyIM.setCookie('trophyim_bosh_xid', TrophyIM.connection.jid + "|" +
            TrophyIM.connection.sid + "|" +  TrophyIM.connection.rid);
            TrophyIM.rosterObj.save();
        }
    },
    /**  Function: showlogin
     *
     *   This function clears out the IM box and either redisplays the login
     *   page, or re-attaches to Strophe, preserving the logging div if it
     *   exists, or creating a new one of we are re-attaching.
     */
    showLogin : function() {
        //JSON is the last script to load, so we wait on it
        //Added Strophe check too because of bug where it's sometimes missing
        if (typeof(JSON) != undefined && typeof(Strophe) != undefined) {
            TrophyIM.JSONStore = new TrophyIMJSONStore();
            if (TrophyIM.JSONStore.store_working && TrophyIM.cookies['trophyim_bosh_xid']) {
                var xids = TrophyIM.cookies['trophyim_bosh_xid'].split("|");
                TrophyIM.delCookie('trophyim_bosh_xid');
                TrophyIM.constants.stale_roster = true;
                if (TrophyIM.cookies['trophyimloglevel']) {
                    TrophyIM.client_div.appendChild(DOMObjects.getHTML('loggingDiv'));
                    TrophyIM.logging_div = document.getElementById('trophyimlog');
                }
                TrophyIM.connection = new Strophe.Connection(TROPHYIM_BOSH_SERVICE);
                TrophyIM.connection.rawInput = TrophyIM.rawInput;
                TrophyIM.connection.rawOutput = TrophyIM.rawOutput;
                Strophe.log = TrophyIM.log;
                Strophe.info('Attempting Strophe attach.');
                TrophyIM.connection.attach(xids[0], xids[1], xids[2],
                TrophyIM.onConnect);
                TrophyIM.onConnect(Strophe.Status.CONNECTED);
            } else {
                var logging_div = TrophyIM.clearClient();
                TrophyIM.client_div.appendChild(DOMObjects.getHTML('loginPage'));
                if(logging_div) {
                    TrophyIM.client_div.appendChild(logging_div);
                    TrophyIM.logging_div =
                    document.getElementById('trophyimlog');
                }
                if (TrophyIM.cookies['trophyimjid']) {
                    document.getElementById('trophyimjid').value =
                    TrophyIM.cookies['trophyimjid'];
                }
                if (TrophyIM.cookies['trophyimloglevel']) {
                    document.getElementById('trophyimloglevel').checked = true;
                }
            }
        } else {
            setTimeout("TrophyIM.showLogin()", 500);
        }
    },
    /** Function: log
     *
     *  This function logs the given message in the trophyimlog div
     *
     *  Parameter: (String) msg - the message to log
     */
    log : function(level, msg) {
        if (TrophyIM.logging_div && level >= TROPHYIM_LOGLEVEL) {
            while(TrophyIM.logging_div.childNodes.length > TROPHYIM_LOG_LINES) {
                TrophyIM.logging_div.removeChild(
                TrophyIM.logging_div.firstChild);
            }
            var msg_div = document.createElement('div');
            msg_div.className = 'trophyimlogitem';
            msg_div.appendChild(document.createTextNode(msg));
            TrophyIM.logging_div.appendChild(msg_div);
            TrophyIM.logging_div.scrollTop = TrophyIM.logging_div.scrollHeight;
        }
    },
    /** Function: rawInput
     *
     *  This logs the packets actually recieved by strophe at the debug level
     */
    rawInput : function (data) {
        Strophe.debug("RECV: " + data);
    },
    /** Function: rawInput
     *
     *  This logs the packets actually recieved by strophe at the debug level
     */
    rawOutput : function (data) {
        Strophe.debug("SEND: " + data);
    },
    /** Function: login
     *
     *  This function logs into server using information given on login page.
     *  Since the login page is where the logging checkbox is, it makes or
     *  removes the logging div and cookie accordingly.
     *
     */
    login : function() {
        if (document.getElementById('trophyimloglevel').checked) {
            TrophyIM.setCookie('trophyimloglevel', 1);
            if (!document.getElementById('trophyimlog')) {
                TrophyIM.client_div.appendChild(DOMObjects.getHTML('loggingDiv'));
                TrophyIM.logging_div = document.getElementById('trophyimlog');
            }
        } else {
            TrophyIM.delCookie('trophyimloglevel');
            if (document.getElementById('trophyimlog')) {
                TrophyIM.client_div.removeChild(document.getElementById(
                'trophyimlog'));
                TrophyIM.logging_div = null;
            }
        }
        if (TrophyIM.JSONStore.store_working) { //In case they never logged out
            TrophyIM.JSONStore.delData(['groups','roster', 'active_chat',
            'chat_history']);
        }
        TrophyIM.connection = new Strophe.Connection(TROPHYIM_BOSH_SERVICE);
        TrophyIM.connection.rawInput = TrophyIM.rawInput;
        TrophyIM.connection.rawOutput = TrophyIM.rawOutput;
        Strophe.log = TrophyIM.log;
        var barejid  = document.getElementById('trophyimjid').value
        var fulljid = barejid + '/TrophyIM';
        TrophyIM.setCookie('trophyimjid', barejid);
        var password = document.getElementById('trophyimpass').value;
        var button = document.getElementById('trophyimconnect');
        if (button.value == 'connect') {
            button.value = 'disconnect';
            TrophyIM.connection.connect(fulljid, password, TrophyIM.onConnect);
        } else {
            button.value = 'connect';
            TrophyIM.connection.disconnect();
        }

    },
    /** Function: login
     *
     *  Logs into fresh session through Strophe, purging any old data.
     */
    logout : function() {
        TrophyIM.delCookie('trophyim_bosh_xid');
        delete TrophyIM['cookies']['trophyim_bosh_xid'];
        if (TrophyIM.JSONStore.store_working) {
            TrophyIM.JSONStore.delData(['groups','roster', 'active_chat',
            'chat_history']);
        }
        for (var chat in TrophyIM.activeChats['divs']) {
            delete TrophyIM.activeChats['divs'][chat];
        }
        TrophyIM.activeChats = {current: null, divs: {}},
        TrophyIM.connection.disconnect();
        TrophyIM.showLogin();
    },
    /** Function onConnect
     *
     *  Callback given to Strophe upon connection to BOSH proxy.
     */
    onConnect : function(status) {
        if (status == Strophe.Status.CONNECTING) {
            Strophe.info('Strophe is connecting.');
        } else if (status == Strophe.Status.CONNFAIL) {
            Strophe.info('Strophe failed to connect.');
            TrophyIM.delCookie('trophyim_bosh_xid');
            TrophyIM.showLogin();
        } else if (status == Strophe.Status.DISCONNECTING) {
            Strophe.info('Strophe is disconnecting.');
        } else if (status == Strophe.Status.DISCONNECTED) {
            Strophe.info('Strophe is disconnected.');
            TrophyIM.delCookie('trophyim_bosh_xid');
            TrophyIM.showLogin();
        } else if (status == Strophe.Status.CONNECTED) {
            Strophe.info('Strophe is connected.');
            TrophyIM.showClient();
        }
    },

    /** Function: showClient
     *
     *  This clears out the main div and puts in the main client.  It also
     *  registers all the handlers for Strophe to call in the client.
     */
    showClient : function() {
        TrophyIM.setCookie('trophyim_bosh_xid', TrophyIM.connection.jid + "|" +
        TrophyIM.connection.sid + "|" +  TrophyIM.connection.rid);
        var logging_div = TrophyIM.clearClient();
        TrophyIM.client_div.appendChild(DOMObjects.getHTML('rosterDiv'));
        TrophyIM.client_div.appendChild(DOMObjects.getHTML('chatArea'));
        TrophyIM.client_div.appendChild(DOMObjects.getHTML('statusDiv'));
        if(logging_div) {
            TrophyIM.client_div.appendChild(logging_div);
            TrophyIM.logging_div = document.getElementById('trophyimlog');
        }
        TrophyIM.rosterObj = new TrophyIMRoster();
        TrophyIM.connection.addHandler(TrophyIM.onVersion, Strophe.NS.VERSION,
        'iq', null, null, null);
        TrophyIM.connection.addHandler(TrophyIM.onRoster, Strophe.NS.ROSTER,
        'iq', null, null, null);
        TrophyIM.connection.addHandler(TrophyIM.onPresence, null, 'presence',
        null, null, null);
        TrophyIM.connection.addHandler(TrophyIM.onMessage, null, 'message',
        null, null,  null);
        //Get roster then announce presence.
        TrophyIM.connection.send($iq({type: 'get', xmlns: Strophe.NS.CLIENT}).c(
        'query', {xmlns: Strophe.NS.ROSTER}).tree());
        TrophyIM.connection.send($pres().tree());
        TrophyIM.renderChats();
        setTimeout("TrophyIM.renderRoster()", 1000);
    },
    /** Function: clearClient
     *
     *  Clears out client div, preserving and returning existing logging_div if
     *  one exists
     */
    clearClient : function() {
        if(TrophyIM.logging_div) {
            var logging_div = TrophyIM.client_div.removeChild(
            document.getElementById('trophyimlog'));
        } else {
            var logging_div = null;
        }
        while(TrophyIM.client_div.childNodes.length > 0) {
            TrophyIM.client_div.removeChild(TrophyIM.client_div.firstChild);
        }
        return logging_div;
    },
    /** Function: onVersion
     *
     *  jabber:iq:version query handler
     */
    onVersion : function(msg) {
        Strophe.debug("Version handler");
        if (msg.getAttribute('type') == 'get') {
            var from = msg.getAttribute('from');
            var to = msg.getAttribute('to');
            var id = msg.getAttribute('id');
            var reply = $iq({type: 'result', to: from, from: to, id: id}).c('query',
            {name: "TrophyIM", version: TROPHYIM_VERSION, os:
            "Javascript-capable browser"});
            TrophyIM.connection.send(reply.tree());
        }
        return true;
    },
    /** Function: onRoster
     *
     *  Roster iq handler
     */
    onRoster : function(msg) {
        Strophe.debug("Roster handler");
        var roster_items = msg.firstChild.getElementsByTagName('item');
        for (var i = 0; i < roster_items.length; i++) {
            var groups = roster_items[i].getElementsByTagName('group');
            var group_array = new Array();
            for (var g = 0; g < groups.length; g++) {
                group_array[group_array.length] =
                groups[g].firstChild.nodeValue;
            }
            TrophyIM.rosterObj.addContact(roster_items[i].getAttribute('jid'),
            roster_items[i].getAttribute('subscription'),
            roster_items[i].getAttribute('name'), group_array);
        }
        if (msg.getAttribute('type') == 'set') {
            TrophyIM.connection.send($iq({type: 'reply', id:
            msg.getAttribute('id'), to: msg.getAttribute('from')}).tree());
        }
        return true;
    },
    /** Function: onPresence
     *
     *  Presence handler
     */
    onPresence : function(msg) {
        Strophe.debug("Presence handler");
        var type = msg.getAttribute('type') ? msg.getAttribute('type') :
        'available';
        var show = msg.getElementsByTagName('show').length ? Strophe.getText(
        msg.getElementsByTagName('show')[0]) : type;
        var status = msg.getElementsByTagName('status').length ? Strophe.getText(
        msg.getElementsByTagName('status')[0]) : '';
        var priority = msg.getElementsByTagName('priority').length ? parseInt(
        Strophe.getText(msg.getElementsByTagName('priority')[0])) : 0;
        TrophyIM.rosterObj.setPresence(msg.getAttribute('from'), priority,
        show, status);
        return true;
    },
    /** Function: onMessage
     *
     *  Message handler
     */
    onMessage : function(msg) {
        Strophe.debug("Message handler");
        var from = msg.getAttribute('from');
        var type = msg.getAttribute('type');
        var elems = msg.getElementsByTagName('body');

        if ((type == 'chat' || type == 'normal') && elems.length > 0) {
            var barejid = Strophe.getBareJidFromJid(from);
            var jid_lower = barejid.toLowerCase();
            var contact = TrophyIM.rosterObj.roster[barejid.toLowerCase()]['contact'];
            if (contact) { //Do we know you?
                if (contact['name'] != null) {
                    message  = contact['name'] + " (" + barejid + "): ";
                } else {
                    message = contact['jid'] + ": ";
                }
                message += Strophe.getText(elems[0]);
                TrophyIM.makeChat(from); //Make sure we have a chat window
                TrophyIM.addMessage(message, jid_lower);
                if (TrophyIM.activeChats['current'] != jid_lower) {
                    TrophyIM.activeChats['divs'][jid_lower][
                    'tab'].className = "trophyimchattab trophyimchattab_a";
                    TrophyIM.setTabPresence(from,
                    TrophyIM.activeChats['divs'][jid_lower]['tab']);
                }
            }
        }
        return true;
    },
    /** Function: makeChat
     *
     *  Make sure chat window to given fulljid exists, switching chat context to
     *  given resource
     */
    makeChat : function(fulljid) {
        var barejid = Strophe.getBareJidFromJid(fulljid);
        if (!TrophyIM.activeChats['divs'][barejid]) {
            var chat_tabs = document.getElementById('trophyimchattabs');
            var chat_tab = DOMObjects.getHTML('chatTab');
            var chat_box = DOMObjects.getHTML('chatBox');
            var contact = TrophyIM.rosterObj.getContact(barejid);
            var tab_name = (contact['name'] != null) ? contact['name'] : barejid;
            chat_tab.className = "trophyimchattab trophyimchattab_a";
            getElementsByClassName('trophyimchattabjid', 'div',
            chat_tab)[0].appendChild(document.createTextNode(barejid));
            getElementsByClassName('trophyimchattabname', 'div',
            chat_tab)[0].appendChild(document.createTextNode(tab_name));
            chat_tab = chat_tabs.appendChild(chat_tab);
            TrophyIM.activeChats['divs'][barejid] = {jid:fulljid, tab:chat_tab,
            box:chat_box};
            if (!TrophyIM.activeChats['current']) { //We're the first
                TrophyIM.activeChats['current'] = barejid;
                document.getElementById('trophyimchat').appendChild(chat_box);
                TrophyIM.activeChats['divs'][barejid]['box'] = chat_box;
                TrophyIM.activeChats['divs'][barejid]['tab'].className =
                "trophyimchattab trophyimchattab_f";
            }
            if (!TrophyIM.chatHistory[barejid.toLowerCase()]) {
                TrophyIM.chatHistory[barejid.toLowerCase()] = {resource: null,
                history: new Array()};
            }
            TrophyIM.setTabPresence(fulljid, chat_tab);
        }
        TrophyIM.activeChats['divs'][barejid.toLowerCase()]['resource'] =
        Strophe.getResourceFromJid(fulljid);
        TrophyIM.chatHistory[barejid.toLowerCase()]['resource'] =
        Strophe.getResourceFromJid(fulljid);
    },
    /** Function showChat
     *
     *  Make chat box to given barejid active
     */
    showChat : function(barejid) {
        if (TrophyIM.activeChats['current'] &&
        TrophyIM.activeChats['current'] != barejid) {
            var chat_area = document.getElementById('trophyimchat');
            var active_divs =
            TrophyIM.activeChats['divs'][TrophyIM.activeChats['current']];
            active_divs['box'] =
            chat_area.removeChild(getElementsByClassName('trophyimchatbox',
            'div', chat_area)[0].parentNode);
            active_divs['tab'].className = "trophyimchattab trophyimchattab_b";
            TrophyIM.setTabPresence(TrophyIM.activeChats['current'],
            active_divs['tab']);
            TrophyIM.activeChats['divs'][barejid]['box'] =
            chat_area.appendChild(TrophyIM.activeChats['divs'][barejid]['box']);
            TrophyIM.activeChats['current'] = barejid;
            TrophyIM.activeChats['divs'][barejid]['tab'].className =
            "trophyimchattab trophyimchattab_f";
            TrophyIM.setTabPresence(barejid,
            TrophyIM.activeChats['divs'][barejid]['tab']);
            getElementsByClassName('trophyimchatinput', null,
            TrophyIM.activeChats['divs'][barejid]['box'])[0].focus();
        }
    },
    /** Function: setTabPresence
     *
     *  Applies appropriate class to tab div based on presence
     *
     *  Parameters:
     *    (String) jid - jid to check presence for
     *    (String) tab_div - tab div element to alter class on
     */
    setTabPresence : function(jid, tab_div) {
        var presence = TrophyIM.rosterObj.getPresence(jid);
        tab_div.className = tab_div.className.replace(" trophyimchattab_av", "");
        tab_div.className = tab_div.className.replace(" trophyimchattab_aw", "");
        tab_div.className = tab_div.className.replace(" trophyimchattab_off", "");
        if (presence) {
            if (presence['show'] == "chat" || presence['show'] == "available") {
                tab_div.className += " trophyimchattab_av";
            } else {
                tab_div.className += " trophyimchattab_aw";
            }
        } else {
            tab_div.className += " trophyimchattab_off";
        }
    },
    /** Function: addMessage
     *
     *  Adds message to chat box, and history
     *
     *  Parameters:
     *    (string) msg - the message to add
     *    (string) jid - the jid of chat box to add the message to.
     */
    addMessage : function(msg, jid) {
        var chat_box = getElementsByClassName('trophyimchatbox', 'div',
        TrophyIM.activeChats['divs'][jid]['box'])[0];
        var msg_div = document.createElement('div');
        msg_div.className = 'trophyimchatmessage';
        msg_div.appendChild(document.createTextNode(msg));
        chat_box.appendChild(msg_div);
        chat_box.scrollTop = chat_box.scrollHeight;
        if (TrophyIM.chatHistory[jid]['history'].length > 10) {
            TrophyIM.chatHistory[jid]['history'].shift();
        }
        TrophyIM.chatHistory[jid]['history'][
        TrophyIM.chatHistory[jid]['history'].length] = msg;
    },
    /** Function: renderRoster
     *
     *  Renders roster, looking only for jids flagged by setPresence as having
     *  changed.
     */
    renderRoster : function() {
        if (TrophyIM.rosterObj.changes.length > 0) {
            var roster_div = document.getElementById('trophyimroster');
            if(roster_div) {
                var groups = new Array();
                for (var group in TrophyIM.rosterObj.groups) {
                    groups[groups.length] = group;
                }
                groups.sort();
                var group_divs = getElementsByClassName('trophyimrostergroup',
                null, roster_div);
                for (var g = 0; g < group_divs.length; g++) {
                    var group_name = getElementsByClassName('trophyimrosterlabel',
                    null, group_divs[g])[0].firstChild.nodeValue;
                    while (group_name > groups[0]) {
                        var new_group = TrophyIM.renderGroup(groups[0], roster_div);
                        new_group = roster_div.insertBefore(new_group,
                        group_divs[g]);
                        if (TrophyIM.rosterObj.groupHasChanges(groups[0])) {
                            TrophyIM.renderGroupUsers(new_group, groups[0],
                            TrophyIM.rosterObj.changes.slice());
                        }
                        groups.shift();
                    }
                    if (group_name == groups[0]) {
                        groups.shift();
                    }
                    if (TrophyIM.rosterObj.groupHasChanges(group_name)) {
                        TrophyIM.renderGroupUsers(group_divs[g], group_name,
                        TrophyIM.rosterObj.changes.slice());
                    }
                }
                while (groups.length) {
                    var group_name = groups.shift();
                    var new_group = TrophyIM.renderGroup(group_name,
                    roster_div);
                    new_group = roster_div.appendChild(new_group);
                    if (TrophyIM.rosterObj.groupHasChanges(group_name)) {
                        TrophyIM.renderGroupUsers(new_group, group_name,
                        TrophyIM.rosterObj.changes.slice());
                    }
                }
            }
            TrophyIM.rosterObj.changes = new Array();
            TrophyIM.constants.stale_roster = false;
        }
        setTimeout("TrophyIM.renderRoster()", 1000);
    },
    /** Function: renderChats
    *
    *  Renders chats found in TrophyIM.chatHistory.  Called upon page reload.
    *  Waits for stale_roster flag to clear before trying to run, so that the
    *  roster exists
    */
    renderChats : function() {
        if (TrophyIM.constants.stale_roster == false) {
            if(TrophyIM.JSONStore.store_working) {
                var data = TrophyIM.JSONStore.getData(['chat_history',
                'active_chat']);
                if (data['active_chat']) {
                    for (var jid in data['chat_history']) {
                        fulljid = jid + "/" + data['chat_history'][jid]['resource'];
                        Strophe.info("Makechat " + fulljid);
                        TrophyIM.makeChat(fulljid);
                        for (var h = 0; h <
                        data['chat_history'][jid]['history'].length; h++) {
                            TrophyIM.addMessage(data['chat_history'][jid]['history'][h],
                            jid);
                        }
                    }
                    TrophyIM.chat_history = data['chat_history'];
                    TrophyIM.showChat(data['active_chat']);
                }
            }
        } else {
            setTimeout("TrophyIM.renderChats()", 1000);
        }
    },
    /** Function: renderGroup
     *
     *  Renders actual group label in roster
     *
     *  Parameters: 
     *    (String) group - name of group to render
     *    (DOM) roster_div - roster div
     *
     *  Returns:
     *    DOM group div to append into roster
     */
    renderGroup : function(group, roster_div) {
        var new_group = DOMObjects.getHTML('rosterGroup');
        var label_div = getElementsByClassName( 'trophyimrosterlabel', null,
        new_group)[0];
        label_div.appendChild(document.createTextNode(group));
        new_group.appendChild(label_div);
        return new_group;
    },
    /** Function: renderGroupUsers
     *
     *  Re-renders user entries in given group div based on status of roster
     *
     *  Parameter: (Array) changes - jids with changes in the roster.  Note:
     *  renderGroupUsers will clobber this.
     */
    renderGroupUsers : function(group_div, group_name, changes) {
        var group_members = TrophyIM.rosterObj.groups[group_name];
        var member_divs = getElementsByClassName('trophyimrosteritem', null,
        group_div);
        for (var m = 0; m < member_divs.length; m++) {
            member_jid = getElementsByClassName('trophyimrosterjid', null,
            member_divs[m])[0].firstChild.nodeValue;
            if (member_jid > changes[0]) {
                if (changes[0] in group_members) {
                    var new_presence = TrophyIM.rosterObj.getPresence(
                    changes[0]);
                    if(new_presence) {
                        var new_member = DOMObjects.getHTML('rosterItem');
                        var new_contact =
                        TrophyIM.rosterObj.getContact(changes[0]);
                        getElementsByClassName('trophyimrosterjid', null,
                        new_member)[0].appendChild(document.createTextNode(
                        changes[0]));
                        var new_name = (new_contact['name'] != null) ?
                        new_contact['name'] : changes[0];
                        getElementsByClassName('trophyimrostername', null,
                        new_member)[0].appendChild(document.createTextNode(
                        new_name));
                        group_div.insertBefore(new_member, member_divs[m]);
                        if (new_presence['show'] == "available" ||
                        new_presence['show'] == "chat") {
                            new_member.className =
                            "trophyimrosteritem trophyimrosteritem_av";
                        } else {
                            new_member.className =
                            "trophyimrosteritem trophyimrosteritem_aw";
                        }
                    } else {
                        //show offline contacts
                    }
                }
                changes.shift();
            } else if (member_jid == changes[0]) {
                member_presence = TrophyIM.rosterObj.getPresence(member_jid);
                if(member_presence) {
                    if (member_presence['show'] == "available" ||
                    member_presence['show'] == "chat") {
                        member_divs[m].className =
                        "trophyimrosteritem trophyimrosteritem_av";
                    } else {
                        member_divs[m].className =
                        "trophyimrosteritem trophyimrosteritem_aw";
                    }
                } else {
                    //show offline status
                    group_div.removeChild(member_divs[m]);
                }
                changes.shift();
            }
        }
        while (changes.length > 0) {
            if (changes[0] in group_members) {
                var new_presence = TrophyIM.rosterObj.getPresence(changes[0]);
                if(new_presence) {
                    var new_member = DOMObjects.getHTML('rosterItem');
                    var new_contact =
                    TrophyIM.rosterObj.getContact(changes[0]);
                    getElementsByClassName('trophyimrosterjid', null,
                    new_member)[0].appendChild(document.createTextNode(
                    changes[0]));
                    var new_name = (new_contact['name'] != null) ?
                    new_contact['name'] : changes[0];
                    getElementsByClassName('trophyimrostername', null,
                    new_member)[0].appendChild(document.createTextNode(
                    new_name));
                    group_div.appendChild(new_member);
                    if (new_presence['show'] == "available" ||
                    new_presence['show'] == "chat") {
                        new_member.className =
                        "trophyimrosteritem trophyimrosteritem_av";
                    } else {
                        new_member.className =
                        "trophyimrosteritem trophyimrosteritem_aw";
                    }
                } else {
                    //show offline
                }
            }
            changes.shift();
        }
    },
    /** Function: rosterClick
     *
     *  Handles actions when a roster item is clicked
     */
    rosterClick : function(roster_item) {
        var barejid = getElementsByClassName('trophyimrosterjid', null,
        roster_item)[0].firstChild.nodeValue;
        var presence = TrophyIM.rosterObj.getPresence(barejid);
        if (presence && presence['resource']) {
            var fulljid = barejid + "/" + presence['resource'];
        } else {
            var fulljid = barejid;
        }
        TrophyIM.makeChat(fulljid);
        TrophyIM.showChat(barejid);
    },
    /** Function: tabClick
     *
     *  Handles actions when a chat tab is clicked
     */
    tabClick : function(tab_item) {
        var barejid = getElementsByClassName('trophyimchattabjid', null,
        tab_item)[0].firstChild.nodeValue;
        if (TrophyIM.activeChats['divs'][barejid]) {
            TrophyIM.showChat(barejid);
        }
    },
    /** Function: tabClose
     *
     *  Closes chat tab
     */
    tabClose : function(tab_item) {
        var barejid = getElementsByClassName('trophyimchattabjid', null,
        tab_item.parentNode)[0].firstChild.nodeValue;
        if (TrophyIM.activeChats['current'] == barejid) {
            if (tab_item.parentNode.nextSibling) {
                TrophyIM.showChat(getElementsByClassName('trophyimchattabjid',
                null, tab_item.parentNode.nextSibling)[0].firstChild.nodeValue);
            } else if (tab_item.parentNode.previousSibling) {
                TrophyIM.showChat(getElementsByClassName('trophyimchattabjid',
                null, tab_item.parentNode.previousSibling)[0].firstChild.nodeValue);
            } else { //no other active chat
                document.getElementById('trophyimchat').removeChild(
                getElementsByClassName('trophyimchatbox')[0].parentNode);
                delete TrophyIM.activeChats['current'];
            }
        }
        delete TrophyIM.activeChats['divs'][barejid];
        delete TrophyIM.chatHistory[barejid];
        //delete tab
        tab_item.parentNode.parentNode.removeChild(tab_item.parentNode);
    },
    /** Function: sendMessage
     *
     *  Send message from chat input to user
     */
    sendMessage : function(chat_box) {
        var message_input =
        getElementsByClassName('trophyimchatinput', null,
        chat_box.parentNode)[0];
        var active_jid = TrophyIM.activeChats['current'];
        if(TrophyIM.activeChats['current']) {
            var active_chat =
            TrophyIM.activeChats['divs'][TrophyIM.activeChats['current']];
            var to = TrophyIM.activeChats['current'];
            if (active_chat['resource']) {
                to += "/" + active_chat['resource'];
            }
            TrophyIM.connection.send($msg({to: to, from:
            TrophyIM.connection.jid, type: 'chat'}).c('body').t(
            message_input.value).tree());
            TrophyIM.addMessage("Me:\n" + message_input.value,
            TrophyIM.activeChats['current']);
        }
        message_input.value = '';
        message_input.focus();
    }
};

/** Class: TrophyIMRoster
 *
 *
 *  This object stores the roster and presence info for the TrophyIMClient
 *
 *  roster[jid_lower]['contact']
 *  roster[jid_lower]['presence'][resource]
 */
function TrophyIMRoster() {
    /** Constants: internal arrays
     *    (Object) roster - the actual roster/presence information
     *    (Object) groups - list of current groups in the roster
     *    (Array) changes - array of jids with presence changes
     */
    if (TrophyIM.JSONStore.store_working) {
        var data = TrophyIM.JSONStore.getData(['roster', 'groups']);
        this.roster = (data['roster'] != null) ? data['roster'] : {};
        this.groups = (data['groups'] != null) ? data['groups'] : {};
    } else {
        this.roster = {};
        this.groups = {};
    }
    this.changes = new Array();
    if (TrophyIM.constants.stale_roster) {
        for (var jid in this.roster) {
            this.changes[this.changes.length] = jid;
        }
    }
    /** Function: addContact
     *
     *  Adds given contact to roster
     *
     *  Parameters:
     *    (String) jid - bare jid
     *    (String) subscription - subscription attribute for contact
     *    (String) name - name attribute for contact
     *    (Array) groups - array of groups contact is member of
     */
    this.addContact = function(jid, subscription, name, groups) {
        var contact = {jid:jid, subscription:subscription, name:name, groups:groups}
        var jid_lower = jid.toLowerCase();
        if (this.roster[jid_lower]) {
            this.roster[jid_lower]['contact'] = contact;
        } else {
            this.roster[jid_lower] = {contact:contact};
        }
        groups = groups ? groups : [''];
        for (var g = 0; g < groups.length; g++) {
            if (!this.groups[groups[g]]) {
                this.groups[groups[g]] = {};
            }
            this.groups[groups[g]][jid_lower] = jid_lower;
        }
    }
    /** Function: getContact
     *
     *  Returns contact entry for given jid
     *
     *  Parameter: (String) jid - jid to return
     */
    this.getContact = function(jid) {
        if (this.roster[jid.toLowerCase()]) {
            return this.roster[jid.toLowerCase()]['contact'];
        }
    }
    /** Function: setPresence
     *
     *  Sets presence
     *
     *  Parameters:
     *    (String) fulljid: full jid with presence
     *    (Integer) priority: priority attribute from presence
     *    (String) show: show attribute from presence
     *    (String) status: status attribute from presence
     */
    this.setPresence = function(fulljid, priority, show, status) {
        var barejid = Strophe.getBareJidFromJid(fulljid);
        var resource = Strophe.getResourceFromJid(fulljid);
        var jid_lower = barejid.toLowerCase();
        if(show != 'unavailable') {
            if (!this.roster[jid_lower]) {
                this.addContact(barejid, 'not-in-roster');
            }
            var presence = {
                resource:resource, priority:priority, show:show, status:status
            }
            if (!this.roster[jid_lower]['presence']) {
                this.roster[jid_lower]['presence'] = {}
            }
            this.roster[jid_lower]['presence'][resource] = presence
        } else if (this.roster[jid_lower] && this.roster[jid_lower]['presence']
        && this.roster[jid_lower]['presence'][resource]) {
            delete this.roster[jid_lower]['presence'][resource];
        }
        this.addChange(jid_lower);
        if (TrophyIM.activeChats['divs'][jid_lower]) {
            TrophyIM.setTabPresence(jid_lower, 
            TrophyIM.activeChats['divs'][jid_lower]['tab']);
        }
    }
    /** Function: addChange
     *
     *  Adds given jid to this.changes, keeping this.changes sorted and
     *  preventing duplicates.
     *
     *  Parameters
     *    (String) jid : jid to add to this.changes
     */
    this.addChange = function(jid) {
        for (var c = 0; c < this.changes.length; c++) {
            if (this.changes[c] == jid) {
                return;
            }
        }
        this.changes[this.changes.length] = jid;
        this.changes.sort();
    }
    /** Function: getPresence
     *
     *  Returns best presence for given jid as Array(resource, priority, show,
     *  status)
     *
     *  Parameter: (String) fulljid - jid to return best presence for
     */
    this.getPresence = function(fulljid) {
        var jid = Strophe.getBareJidFromJid(fulljid);
        var current = null;
        if (this.roster[jid.toLowerCase()] &&
        this.roster[jid.toLowerCase()]['presence']) {
            for (var resource in this.roster[jid.toLowerCase()]['presence']) {
                var presence = this.roster[jid.toLowerCase()]['presence'][resource];
                if (current == null) {
                    current = presence
                } else {
                    if(presence['priority'] > current['priority'] && ((presence['show'] == "chat"
                    || presence['show'] == "available") || (current['show'] != "chat" ||
                    current['show'] != "available"))) {
                        current = presence
                    }
                }
            }
        }
        return current;
    }
    /** Function: groupHasChanges
     *
     *  Returns true if current group has members in this.changes
     *
     *  Parameters:
     *    (String) group - name of group to check
     */
    this.groupHasChanges = function(group) {
        for (var c = 0; c < this.changes.length; c++) {
            if (this.groups[group][this.changes[c]]) {
                return true;
            }
        }
        return false;
    }
    /** Fuction: save
     *
     *  Saves roster data to JSON store
     */
    this.save = function() {
        if (TrophyIM.JSONStore.store_working) {
            TrophyIM.JSONStore.setData({roster:this.roster,
            groups:this.groups, active_chat:TrophyIM.activeChats['current'],
            chat_history:TrophyIM.chatHistory});
        }
    }
}
/** Class: TrophyIMJSONStore
 *
 *
 *  This object is the mechanism by which TrophyIM stores and retrieves its
 *  variables from the url provided by TROPHYIM_JSON_STORE
 *
 */
function TrophyIMJSONStore() {
    this.store_working = false;
    /** Function _newXHR
     *
     *  Set up new cross-browser xmlhttprequest object
     *
     *  Parameters:
     *    (function) handler = what to set onreadystatechange to
     */
     this._newXHR = function (handler) {
        var xhr = null;
        if (window.XMLHttpRequest) {
            xhr = new XMLHttpRequest();
            if (xhr.overrideMimeType) {
            xhr.overrideMimeType("text/xml");
            }
        } else if (window.ActiveXObject) {
            xhr = new ActiveXObject("Microsoft.XMLHTTP");
        }
        return xhr;
    }
    /** Function getData
     *  Gets data from JSONStore
     *
     *  Parameters:
     *    (Array) vars = Variables to get from JSON store
     *
     *  Returns:
     *    Object with variables indexed by names given in parameter 'vars'
     */
    this.getData = function(vars) {
        if (typeof(TROPHYIM_JSON_STORE) != undefined) {
            Strophe.debug("Retrieving JSONStore data");
            var xhr = this._newXHR();
            var getdata = "get=" + vars.join(",");
            try {
                xhr.open("POST", TROPHYIM_JSON_STORE, false);
            } catch (e) {
                Strophe.error("JSONStore open failed.");
                return false;
            }
            xhr.setRequestHeader('Content-type',
            'application/x-www-form-urlencoded');
            xhr.setRequestHeader('Content-length', getdata.length);
            xhr.send(getdata);
            if (xhr.readyState == 4 && xhr.status == 200) {
                try {
                    var dataObj = JSON.parse(xhr.responseText);
                    return this.emptyFix(dataObj);
                } catch(e) {
                    Strophe.error("Could not parse JSONStore response" +
                    xhr.responseText);
                    return false;
                }
            } else {
                Strophe.error("JSONStore open failed. Status: " + xhr.status);
                return false;
            }
        }
    }
    /** Function emptyFix
     *    Fix for bugs in external JSON implementations such as
     *    http://bugs.php.net/bug.php?id=41504.
     *    A.K.A. Don't use PHP, people.
     */
    this.emptyFix = function(obj) {
        if (typeof(obj) == "object") {
            for (var i in obj) {
                if (i == '_empty_') {
                    obj[""] = this.emptyFix(obj['_empty_']);
                    delete obj['_empty_'];
                } else {
                    obj[i] = this.emptyFix(obj[i]);
                }
            }
        }
        return obj
    }
    /** Function delData
     *    Deletes data from JSONStore
     * 
     *  Parameters:
     *    (Array) vars  = Variables to delete from JSON store
     *
     *  Returns:
     *    Status of delete attempt.
     */
    this.delData = function(vars) {
        if (typeof(TROPHYIM_JSON_STORE) != undefined) {
            Strophe.debug("Retrieving JSONStore data");
            var xhr = this._newXHR();
            var deldata = "del=" + vars.join(",");
            try {
                xhr.open("POST", TROPHYIM_JSON_STORE, false);
            } catch (e) {
                Strophe.error("JSONStore open failed.");
                return false;
            }
            xhr.setRequestHeader('Content-type',
            'application/x-www-form-urlencoded');
            xhr.setRequestHeader('Content-length', deldata.length);
            xhr.send(deldata);
            if (xhr.readyState == 4 && xhr.status == 200) {
                try {
                    var dataObj = JSON.parse(xhr.responseText);
                    return dataObj;
                } catch(e) {
                    Strophe.error("Could not parse JSONStore response");
                    return false;
                }
            } else {
                Strophe.error("JSONStore open failed. Status: " + xhr.status);
                return false;
            }
        }
    }
    /** Function setData
     *    Stores data in JSONStore, overwriting values if they exist
     *
     *  Parameters:
     *    (Object) vars : Object containing named vars to store ({name: value,
     *    othername: othervalue})
     *
     *  Returns:
     *    Status of storage attempt
     */
    this.setData = function(vars) {
        if (typeof(TROPHYIM_JSON_STORE) != undefined) {
            Strophe.debug("Storing JSONStore data");
            var senddata = "set=" + JSON.stringify(vars);
            var xhr = this._newXHR();
            try {
                xhr.open("POST", TROPHYIM_JSON_STORE, false);
            } catch (e) {
                Strophe.error("JSONStore open failed.");
                return false;
            }
            xhr.setRequestHeader('Content-type',
            'application/x-www-form-urlencoded');
            xhr.setRequestHeader('Content-length', senddata.length);
            xhr.send(senddata);
            if (xhr.readyState == 4 && xhr.status == 200 && xhr.responseText ==
            "OK") {
                return true;
            } else {
                Strophe.error("JSONStore open failed. Status: " + xhr.status);
                return false;
            }
        }
    }
    var testData = true;
    if (this.setData({testData:testData})) {
        var testResult = this.getData(['testData']);
        if (testResult && testResult['testData'] == true) {
            this.store_working = true;
        }
    }
}
/** Constants: Node types
 *
 * Implementations of constants that IE doesn't have, but we need.
 */
if (document.ELEMENT_NODE == null) {
    document.ELEMENT_NODE = 1;
    document.ATTRIBUTE_NODE = 2;
    document.TEXT_NODE = 3;
    document.CDATA_SECTION_NODE = 4;
    document.ENTITY_REFERENCE_NODE = 5;
    document.ENTITY_NODE = 6;
    document.PROCESSING_INSTRUCTION_NODE = 7;
    document.COMMENT_NODE = 8;
    document.DOCUMENT_NODE = 9;
    document.DOCUMENT_TYPE_NODE = 10;
    document.DOCUMENT_FRAGMENT_NODE = 11;
    document.NOTATION_NODE = 12;
}

/** Function: importNode
 *
 *  document.importNode implementation for IE, which doesn't have importNode
 *
 *  Parameters:
 *    (Object) node - dom object
 *    (Boolean) allChildren - import node's children too
 */
if (!document.importNode) {
    document.importNode = function(node, allChildren) {
        switch (node.nodeType) {
            case document.ELEMENT_NODE:
                var newNode = document.createElement(node.nodeName);
                if (node.attributes && node.attributes.length > 0) {
                    for(var i = 0; i < node.attributes.length; i++) {
                        newNode.setAttribute(node.attributes[i].nodeName,
                        node.getAttribute(node.attributes[i].nodeName));
                    }
                }
                if (allChildren && node.childNodes &&
                node.childNodes.length > 0) {
                    for (var i = 0; i < node.childNodes.length; i++) {
                        newNode.appendChild(document.importNode(
                        node.childNodes[i], allChildren));
                    }
                }
                return newNode;
                break;
            case document.TEXT_NODE:
            case document.CDATA_SECTION_NODE:
            case document.COMMENT_NODE:
                return document.createTextNode(node.nodeValue);
                break;
        }
    };
}

/** Function: getElementsByClassName
 *
 *  DOMObject.getElementsByClassName implementation for browsers that don't
 *  support it yet.
 *
 *  Developed by Robert Nyman, http://www.robertnyman.com
 *  Code/licensing: http://code.google.com/p/getelementsbyclassname/
*/
var getElementsByClassName = function (className, tag, elm){
    if (document.getElementsByClassName) {
        getElementsByClassName = function (className, tag, elm) {
            elm = elm || document;
            var elements = elm.getElementsByClassName(className),
                nodeName = (tag)? new RegExp("\\b" + tag + "\\b", "i") : null,
                returnElements = [],
                current;
            for(var i=0, il=elements.length; i<il; i+=1){
                current = elements[i];
                if(!nodeName || nodeName.test(current.nodeName)) {
                    returnElements.push(current);
                }
            }
            return returnElements;
        };
    } else if (document.evaluate) {
        getElementsByClassName = function (className, tag, elm) {
            tag = tag || "*";
            elm = elm || document;
            var classes = className.split(" "),
                classesToCheck = "",
                xhtmlNamespace = "http://www.w3.org/1999/xhtml",
                namespaceResolver = (document.documentElement.namespaceURI ===
                    xhtmlNamespace)? xhtmlNamespace : null,
                returnElements = [],
                elements,
                node;
            for(var j=0, jl=classes.length; j<jl; j+=1){
                classesToCheck += "[contains(concat(' ', @class, ' '), ' " +
                    classes[j] + " ')]";
            }
            try {
                elements = document.evaluate(".//" + tag + classesToCheck,
                    elm, namespaceResolver, 0, null);
            } catch (e) {
                elements = document.evaluate(".//" + tag + classesToCheck,
                    elm, null, 0, null);
            }
            while ((node = elements.iterateNext())) {
                returnElements.push(node);
            }
            return returnElements;
        };
    } else {
        getElementsByClassName = function (className, tag, elm) {
            tag = tag || "*";
            elm = elm || document;
            var classes = className.split(" "),
                classesToCheck = [],
                elements = (tag === "*" && elm.all)? elm.all :
                     elm.getElementsByTagName(tag),
                current,
                returnElements = [],
                match;
            for(var k=0, kl=classes.length; k<kl; k+=1){
                classesToCheck.push(new RegExp("(^|\\s)" + classes[k] +
                    "(\\s|$)"));
            }
            for(var l=0, ll=elements.length; l<ll; l+=1){
                current = elements[l];
                match = false;
                for(var m=0, ml=classesToCheck.length; m<ml; m+=1){
                    match = classesToCheck[m].test(current.className);
                    if (!match) {
                        break;
                    }
                }
                if (match) {
                    returnElements.push(current);
                }
            }
            return returnElements;
        };
    }
    return getElementsByClassName(className, tag, elm);
};

/**
 *
 * Bootstrap self into window.onload and window.onunload
 */
var oldonload = window.onload;
window.onload = function() {
    if(oldonload) {
        oldonload();
    }
    TrophyIM.load();
};
var oldonunload = window.onunload;
window.onunload = function() {
    if(oldonunload) {
        oldonunload();
    }
    TrophyIM.storeData();
}
