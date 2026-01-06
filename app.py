from flask import Flask, render_template, request, jsonify, send_file
import json
import urllib.parse
from datetime import datetime
import re
import io

app = Flask(__name__)

# Enhanced Google Dorks Database - More Aggressive
def get_default_dorks():
    return {
        "categories": {
            "📄 Files & Documents": [
                {"name": "PDF Files", "dork": 'site:{domain} filetype:pdf', "desc": "Find all PDF documents"},
                {"name": "Excel Files", "dork": 'site:{domain} (filetype:xls OR filetype:xlsx OR filetype:xlsm)', "desc": "Find Excel spreadsheets"},
                {"name": "Word Documents", "dork": 'site:{domain} (filetype:doc OR filetype:docx OR filetype:rtf)', "desc": "Find Word documents"},
                {"name": "PowerPoint", "dork": 'site:{domain} (filetype:ppt OR filetype:pptx OR filetype:pps)', "desc": "Find presentations"},
                {"name": "Text Files", "dork": 'site:{domain} (filetype:txt OR filetype:log OR filetype:md)', "desc": "Find text files"},
                {"name": "CSV Files", "dork": 'site:{domain} filetype:csv', "desc": "Find CSV data files"},
                {"name": "SQL Files", "dork": 'site:{domain} (filetype:sql OR filetype:dump)', "desc": "Find SQL dump files"},
                {"name": "XML Files", "dork": 'site:{domain} (filetype:xml OR filetype:xsd OR filetype:wsdl)', "desc": "Find XML files"},
                {"name": "JSON Files", "dork": 'site:{domain} (filetype:json OR filetype:jsonl)', "desc": "Find JSON files"},
                {"name": "Log Files", "dork": 'site:{domain} (filetype:log OR inurl:log OR inurl:logs)', "desc": "Find log files"},
                {"name": "Backup Files", "dork": 'site:{domain} (filetype:bak OR filetype:old OR filetype:backup OR filetype:swp OR filetype:~)', "desc": "Find backup files"},
                {"name": "Archive Files", "dork": 'site:{domain} (filetype:zip OR filetype:rar OR filetype:tar OR filetype:gz OR filetype:7z)', "desc": "Find archive files"},
                {"name": "Database Dumps", "dork": 'site:{domain} (filetype:sql OR filetype:db OR filetype:dbf OR filetype:mdb) (dump OR backup OR database)', "desc": "Find database backups"},
            ],
            "🔐 Sensitive Information": [
                {"name": "Email Addresses", "dork": 'site:{domain} (intext:"@{domain}" OR intext:"email" OR intext:"contact")', "desc": "Find email addresses"},
                {"name": "Phone Numbers", "dork": 'site:{domain} (intext:"phone" OR intext:"mobile" OR intext:"tel:" OR intext:"fax")', "desc": "Find phone numbers"},
                {"name": "Passwords in URLs", "dork": 'site:{domain} (inurl:password OR inurl:passwd OR inurl:pwd OR inurl:pass)', "desc": "Find password-related pages"},
                {"name": "Password Files", "dork": 'site:{domain} (filetype:txt OR filetype:log OR filetype:cfg) (password OR passwd OR pwd OR credentials)', "desc": "Find password files"},
                {"name": "Admin Pages", "dork": 'site:{domain} (inurl:admin OR inurl:administrator OR inurl:cpanel OR inurl:webmaster OR inurl:sysadmin)', "desc": "Find admin interfaces"},
                {"name": "Login Pages", "dork": 'site:{domain} (inurl:login OR inurl:signin OR inurl:auth OR inurl:authenticate OR inurl:logon)', "desc": "Find login pages"},
                {"name": "Config Files", "dork": 'site:{domain} (filetype:conf OR filetype:config OR filetype:cfg OR filetype:ini OR filetype:properties)', "desc": "Find configuration files"},
                {"name": "Database Files", "dork": 'site:{domain} (filetype:sql OR filetype:db OR filetype:mdb OR filetype:sqlite OR filetype:sqlite3 OR filetype:pdb)', "desc": "Find database files"},
                {"name": "API Keys Exposed", "dork": 'site:{domain} (intext:"api_key" OR intext:"apikey" OR intext:"api-key" OR intext:"api_secret" OR intext:"apiSecret")', "desc": "Find API keys"},
                {"name": "AWS Credentials", "dork": 'site:{domain} (intext:"AKIA" OR intext:"aws_access_key_id" OR intext:"aws_secret_access_key" OR intext:"AWS_SESSION_TOKEN")', "desc": "Find AWS credentials"},
                {"name": "Private Keys", "dork": 'site:{domain} (filetype:pem OR filetype:key OR filetype:ppk OR filetype:p12 OR filetype:pfx OR intext:"BEGIN RSA PRIVATE KEY" OR intext:"BEGIN PRIVATE KEY")', "desc": "Find private keys"},
                {"name": "SSH Keys", "dork": 'site:{domain} (filetype:pub OR intext:"ssh-rsa" OR intext:"ssh-ed25519" OR intext:"BEGIN OPENSSH PRIVATE KEY")', "desc": "Find SSH keys"},
                {"name": "Credentials Exposed", "dork": 'site:{domain} (intext:"username" AND intext:"password") OR (intext:"user" AND intext:"pass")', "desc": "Find credentials"},
                {"name": "Secret Files", "dork": 'site:{domain} (inurl:secret OR inurl:private OR inurl:hidden OR inurl:confidential)', "desc": "Find secret files"},
                {"name": "Token Exposure", "dork": 'site:{domain} (intext:"token" OR intext:"bearer" OR intext:"jwt" OR intext:"access_token" OR intext:"refresh_token")', "desc": "Find tokens"},
                {"name": "OAuth Secrets", "dork": 'site:{domain} (intext:"client_secret" OR intext:"clientSecret" OR intext:"oauth" OR intext:"consumer_key")', "desc": "Find OAuth secrets"},
            ],
            "🛡️ Security Vulnerabilities": [
                {"name": "Directory Listing", "dork": 'site:{domain} intitle:"index of" (parent directory OR directory listing)', "desc": "Find open directories"},
                {"name": "Directory Browsing", "dork": 'site:{domain} intitle:"index of /" OR intitle:"index of /admin" OR intitle:"index of /backup"', "desc": "Find directory browsing"},
                {"name": "Error Messages", "dork": 'site:{domain} (intext:"error" OR intext:"warning" OR intext:"exception" OR intext:"fatal" OR intext:"stack trace")', "desc": "Find error messages"},
                {"name": "SQL Errors", "dork": 'site:{domain} (intext:"sql syntax" OR intext:"mysql_fetch" OR intext:"ORA-" OR intext:"PostgreSQL" OR intext:"sqlite3" OR intext:"ODBC")', "desc": "Find SQL error messages"},
                {"name": "PHP Errors", "dork": 'site:{domain} (intext:"PHP Parse error" OR intext:"PHP Warning" OR intext:"PHP Error" OR intext:"Fatal error" OR intext:"on line")', "desc": "Find PHP errors"},
                {"name": "ASP Errors", "dork": 'site:{domain} (intext:"ASP.NET" AND intext:"error") OR intext:"Server Error in"', "desc": "Find ASP.NET errors"},
                {"name": "Server Info", "dork": 'site:{domain} (intitle:"Apache" OR intitle:"nginx" OR intitle:"IIS" OR intitle:"lighttpd" OR intitle:"Server Status")', "desc": "Find server information"},
                {"name": "phpinfo() Exposed", "dork": 'site:{domain} (inurl:phpinfo.php OR intitle:"phpinfo()" OR intext:"PHP Version")', "desc": "Find PHP info pages"},
                {"name": "Git Exposed", "dork": 'site:{domain} (inurl:".git" OR inurl:".gitignore" OR inurl:".gitconfig" OR intitle:"index of /.git")', "desc": "Find exposed Git repositories"},
                {"name": "SVN Exposed", "dork": 'site:{domain} (inurl:".svn" OR intitle:"index of /.svn" OR inurl:".svn/entries")', "desc": "Find exposed SVN repositories"},
                {"name": "Htaccess Exposed", "dork": 'site:{domain} (inurl:.htaccess OR inurl:.htpasswd OR filetype:htaccess)', "desc": "Find .htaccess files"},
                {"name": "ENV Files", "dork": 'site:{domain} (filetype:env OR inurl:.env OR inurl:".env.local" OR inurl:".env.prod" OR inurl:".env.dev")', "desc": "Find environment files"},
                {"name": "DS_Store Files", "dork": 'site:{domain} (inurl:.DS_Store OR filetype:DS_Store)', "desc": "Find DS_Store files"},
                {"name": "Backup Source", "dork": 'site:{domain} (inurl:backup OR inurl:bkp OR inurl:old OR inurl:save) (filetype:php OR filetype:asp OR filetype:aspx)', "desc": "Find backup source files"},
                {"name": "Debug Mode", "dork": 'site:{domain} (intext:"debug" OR inurl:debug OR intext:"DEBUG = True" OR intext:"APP_DEBUG")', "desc": "Find debug mode enabled"},
                {"name": "Trace Logs", "dork": 'site:{domain} (inurl:trace OR inurl:debug OR filetype:trace) intext:"trace"', "desc": "Find trace logs"},
            ],
            "🔧 Admin & Control Panels": [
                {"name": "Swagger/API Docs", "dork": 'site:{domain} (inurl:swagger OR inurl:api-docs OR intitle:"Swagger UI" OR inurl:openapi)', "desc": "Find API documentation"},
                {"name": "GraphQL", "dork": 'site:{domain} (inurl:graphql OR inurl:graphiql OR intitle:"GraphQL Playground")', "desc": "Find GraphQL endpoints"},
                {"name": "Jenkins", "dork": 'site:{domain} (intitle:"Dashboard [Jenkins]" OR inurl:jenkins OR intext:"Jenkins ver")', "desc": "Find Jenkins installations"},
                {"name": "GitLab", "dork": 'site:{domain} (intitle:"GitLab" OR inurl:gitlab)', "desc": "Find GitLab installations"},
                {"name": "Kibana", "dork": 'site:{domain} (intitle:"Kibana" OR inurl:kibana OR inurl:app/kibana)', "desc": "Find Kibana dashboards"},
                {"name": "Grafana", "dork": 'site:{domain} (intitle:"Grafana" OR inurl:grafana)', "desc": "Find Grafana dashboards"},
                {"name": "phpMyAdmin", "dork": 'site:{domain} (intitle:"phpMyAdmin" OR inurl:phpmyadmin OR inurl:pma)', "desc": "Find phpMyAdmin"},
                {"name": "Adminer", "dork": 'site:{domain} (intitle:"Adminer" OR inurl:adminer.php)', "desc": "Find Adminer"},
                {"name": "cPanel", "dork": 'site:{domain} (intitle:"cPanel" OR inurl:cpanel OR inurl:2082 OR inurl:2083)', "desc": "Find cPanel"},
                {"name": "Plesk", "dork": 'site:{domain} (intitle:"Plesk" OR inurl:plesk OR inurl:8443)', "desc": "Find Plesk"},
                {"name": "Webmin", "dork": 'site:{domain} (intitle:"Webmin" OR inurl:webmin OR inurl:10000)', "desc": "Find Webmin"},
                {"name": "WordPress Admin", "dork": 'site:{domain} (inurl:wp-admin OR inurl:wp-login OR inurl:wp-content/plugins)', "desc": "Find WordPress admin"},
                {"name": "Drupal Admin", "dork": 'site:{domain} (inurl:user/login OR inurl:admin/content OR inurl:/node/add)', "desc": "Find Drupal admin"},
                {"name": "Joomla Admin", "dork": 'site:{domain} (inurl:administrator/index.php OR inurl:/administrator/)', "desc": "Find Joomla admin"},
                {"name": "Magento Admin", "dork": 'site:{domain} (inurl:admin OR inurl:adminhtml) intitle:"Magento"', "desc": "Find Magento admin"},
                {"name": "Tomcat Manager", "dork": 'site:{domain} (intitle:"Tomcat" OR inurl:/manager/html OR inurl:tomcat)', "desc": "Find Tomcat manager"},
                {"name": "JBoss Console", "dork": 'site:{domain} (intitle:"JBoss" OR inurl:jmx-console OR inurl:web-console)', "desc": "Find JBoss console"},
                {"name": "WebLogic", "dork": 'site:{domain} (intitle:"WebLogic" OR inurl:console OR inurl:wls)', "desc": "Find WebLogic console"},
            ],
            "📁 Exposed Directories & Paths": [
                {"name": "Upload Directories", "dork": 'site:{domain} (intitle:"index of" (upload OR uploads OR files OR documents))', "desc": "Find upload directories"},
                {"name": "Backup Directories", "dork": 'site:{domain} (intitle:"index of" (backup OR backups OR bak OR old))', "desc": "Find backup directories"},
                {"name": "Config Directories", "dork": 'site:{domain} (intitle:"index of" (config OR conf OR cfg OR settings))', "desc": "Find config directories"},
                {"name": "Log Directories", "dork": 'site:{domain} (intitle:"index of" (log OR logs OR debug))', "desc": "Find log directories"},
                {"name": "Admin Directories", "dork": 'site:{domain} (intitle:"index of" (admin OR administrator OR adm))', "desc": "Find admin directories"},
                {"name": "Include Directories", "dork": 'site:{domain} (intitle:"index of" (include OR includes OR inc))', "desc": "Find include directories"},
                {"name": "Temp Directories", "dork": 'site:{domain} (intitle:"index of" (tmp OR temp OR cache))', "desc": "Find temp directories"},
                {"name": "Private Directories", "dork": 'site:{domain} (intitle:"index of" (private OR secret OR hidden))', "desc": "Find private directories"},
                {"name": "Database Directories", "dork": 'site:{domain} (intitle:"index of" (db OR database OR sql OR data))', "desc": "Find database directories"},
                {"name": "Script Directories", "dork": 'site:{domain} (intitle:"index of" (cgi-bin OR scripts OR bin))', "desc": "Find script directories"},
            ],
            "🔑 Authentication & Sessions": [
                {"name": "Session Files", "dork": 'site:{domain} (filetype:session OR inurl:session OR inurl:sess_)', "desc": "Find session files"},
                {"name": "Cookie Files", "dork": 'site:{domain} (filetype:cookie OR inurl:cookie)', "desc": "Find cookie files"},
                {"name": "Auth Tokens", "dork": 'site:{domain} (inurl:token OR inurl:auth OR inurl:oauth) filetype:json', "desc": "Find auth tokens"},
                {"name": "JWT Tokens", "dork": 'site:{domain} (intext:"eyJ" OR intext:"JWT" OR inurl:jwt)', "desc": "Find JWT tokens"},
                {"name": "Reset Password", "dork": 'site:{domain} (inurl:reset OR inurl:forgot OR inurl:recover) (password OR passwd)', "desc": "Find password reset"},
                {"name": "Registration Pages", "dork": 'site:{domain} (inurl:register OR inurl:signup OR inurl:join OR inurl:create-account)', "desc": "Find registration pages"},
                {"name": "SSO/SAML", "dork": 'site:{domain} (inurl:sso OR inurl:saml OR inurl:adfs OR inurl:shibboleth)', "desc": "Find SSO endpoints"},
                {"name": "LDAP Config", "dork": 'site:{domain} (intext:"ldap" OR inurl:ldap) (config OR configuration OR settings)', "desc": "Find LDAP config"},
            ],
            "🌐 Subdomains & Infrastructure": [
                {"name": "All Subdomains", "dork": 'site:*.{domain} -www', "desc": "Find all subdomains"},
                {"name": "Development Sites", "dork": 'site:dev.{domain} OR site:development.{domain} OR site:staging.{domain} OR site:stage.{domain} OR site:test.{domain} OR site:testing.{domain} OR site:qa.{domain} OR site:uat.{domain}', "desc": "Find development environments"},
                {"name": "Old/Legacy Sites", "dork": 'site:old.{domain} OR site:legacy.{domain} OR site:archive.{domain} OR site:backup.{domain} OR site:v1.{domain} OR site:v2.{domain}', "desc": "Find old/archived sites"},
                {"name": "API Endpoints", "dork": 'site:api.{domain} OR site:api2.{domain} OR site:api-v1.{domain} OR site:api-v2.{domain} OR site:rest.{domain}', "desc": "Find API endpoints"},
                {"name": "Admin Subdomains", "dork": 'site:admin.{domain} OR site:administrator.{domain} OR site:manage.{domain} OR site:panel.{domain} OR site:cms.{domain}', "desc": "Find admin subdomains"},
                {"name": "Mail Servers", "dork": 'site:mail.{domain} OR site:webmail.{domain} OR site:email.{domain} OR site:smtp.{domain} OR site:imap.{domain} OR site:pop.{domain}', "desc": "Find mail servers"},
                {"name": "VPN/Remote Access", "dork": 'site:vpn.{domain} OR site:remote.{domain} OR site:gateway.{domain} OR site:citrix.{domain} OR site:rdp.{domain}', "desc": "Find VPN/remote access"},
                {"name": "CDN/Static Assets", "dork": 'site:cdn.{domain} OR site:static.{domain} OR site:assets.{domain} OR site:images.{domain} OR site:media.{domain}', "desc": "Find CDN/static assets"},
                {"name": "Internal Tools", "dork": 'site:internal.{domain} OR site:intranet.{domain} OR site:portal.{domain} OR site:tools.{domain} OR site:wiki.{domain}', "desc": "Find internal tools"},
                {"name": "Monitoring", "dork": 'site:monitor.{domain} OR site:monitoring.{domain} OR site:status.{domain} OR site:health.{domain} OR site:metrics.{domain}', "desc": "Find monitoring systems"},
                {"name": "Database Servers", "dork": 'site:db.{domain} OR site:database.{domain} OR site:mysql.{domain} OR site:postgres.{domain} OR site:mongo.{domain}', "desc": "Find database servers"},
                {"name": "CI/CD Systems", "dork": 'site:jenkins.{domain} OR site:ci.{domain} OR site:build.{domain} OR site:deploy.{domain} OR site:gitlab.{domain}', "desc": "Find CI/CD systems"},
            ],
            "💻 Source Code & Repositories": [
                {"name": "Source Code Files", "dork": 'site:{domain} (filetype:php OR filetype:asp OR filetype:aspx OR filetype:jsp OR filetype:py OR filetype:rb)', "desc": "Find source code files"},
                {"name": "JavaScript Files", "dork": 'site:{domain} (filetype:js OR filetype:jsx OR filetype:ts OR filetype:tsx) -jquery -bootstrap', "desc": "Find JavaScript files"},
                {"name": "Config Source", "dork": 'site:{domain} (filetype:yml OR filetype:yaml OR filetype:toml OR filetype:properties)', "desc": "Find config files"},
                {"name": "Docker Files", "dork": 'site:{domain} (filetype:dockerfile OR inurl:Dockerfile OR inurl:docker-compose)', "desc": "Find Docker files"},
                {"name": "Kubernetes", "dork": 'site:{domain} (filetype:yaml (kubernetes OR kubectl OR helm) OR inurl:k8s)', "desc": "Find Kubernetes configs"},
                {"name": "Terraform", "dork": 'site:{domain} (filetype:tf OR filetype:tfvars OR filetype:tfstate)', "desc": "Find Terraform files"},
                {"name": "Ansible", "dork": 'site:{domain} (filetype:yml OR filetype:yaml) (ansible OR playbook OR inventory)', "desc": "Find Ansible files"},
                {"name": "Package Files", "dork": 'site:{domain} (filetype:json (package OR composer OR bower) OR filetype:lock)', "desc": "Find package files"},
                {"name": "Requirements", "dork": 'site:{domain} (filetype:txt requirements OR filetype:pip OR Pipfile)', "desc": "Find Python requirements"},
                {"name": "Gemfile", "dork": 'site:{domain} (inurl:Gemfile OR filetype:gemspec)', "desc": "Find Ruby Gemfiles"},
            ],
            "👥 Social & People Intelligence": [
                {"name": "LinkedIn Employees", "dork": 'site:linkedin.com/in "{company}" OR site:linkedin.com "{domain}"', "desc": "Find employees on LinkedIn"},
                {"name": "LinkedIn Company", "dork": 'site:linkedin.com/company "{company}"', "desc": "Find company page"},
                {"name": "GitHub Organization", "dork": 'site:github.com "{company}" OR site:github.com "{domain}"', "desc": "Find GitHub repos"},
                {"name": "GitHub Code", "dork": 'site:github.com "{domain}" (password OR secret OR api_key OR token)', "desc": "Find secrets in GitHub"},
                {"name": "GitLab Code", "dork": 'site:gitlab.com "{domain}" (password OR secret OR api_key OR token)', "desc": "Find secrets in GitLab"},
                {"name": "Pastebin Leaks", "dork": 'site:pastebin.com "{domain}" OR site:paste.org "{domain}"', "desc": "Find Pastebin leaks"},
                {"name": "Trello Boards", "dork": 'site:trello.com "{company}" OR site:trello.com "{domain}"', "desc": "Find Trello boards"},
                {"name": "Slack Channels", "dork": 'site:slack.com "{company}" OR "{domain}" slack invite', "desc": "Find Slack info"},
                {"name": "Discord Servers", "dork": 'site:discord.com "{company}" OR site:discord.gg "{company}"', "desc": "Find Discord servers"},
                {"name": "Stack Overflow", "dork": 'site:stackoverflow.com "{domain}"', "desc": "Find Stack Overflow mentions"},
                {"name": "Reddit Mentions", "dork": 'site:reddit.com "{company}" OR site:reddit.com "{domain}"', "desc": "Find Reddit discussions"},
                {"name": "Twitter/X", "dork": 'site:twitter.com "{company}" OR site:x.com "{company}"', "desc": "Find Twitter mentions"},
                {"name": "Facebook", "dork": 'site:facebook.com "{company}"', "desc": "Find Facebook pages"},
                {"name": "Instagram", "dork": 'site:instagram.com "{company}"', "desc": "Find Instagram profiles"},
                {"name": "YouTube", "dork": 'site:youtube.com "{company}"', "desc": "Find YouTube channels"},
            ],
            "🚨 Critical Exposures": [
                {"name": "Database Credentials", "dork": 'site:{domain} (intext:"mysql" OR intext:"postgresql" OR intext:"mongodb") (intext:"password" OR intext:"passwd" OR intext:"pwd")', "desc": "Find DB credentials"},
                {"name": "FTP Credentials", "dork": 'site:{domain} (intext:"ftp" OR inurl:ftp) (intext:"password" OR intext:"login")', "desc": "Find FTP credentials"},
                {"name": "SMTP Credentials", "dork": 'site:{domain} (intext:"smtp" OR intext:"mail") (intext:"password" OR intext:"credentials")', "desc": "Find SMTP credentials"},
                {"name": "Credit Cards", "dork": 'site:{domain} (intext:"credit card" OR intext:"card number" OR intext:"cvv" OR intext:"expiry")', "desc": "Find credit card info"},
                {"name": "SSN/ID Numbers", "dork": 'site:{domain} (intext:"ssn" OR intext:"social security" OR intext:"national id")', "desc": "Find SSN/ID numbers"},
                {"name": "Medical Records", "dork": 'site:{domain} (intext:"patient" OR intext:"medical" OR intext:"diagnosis" OR intext:"prescription")', "desc": "Find medical records"},
                {"name": "Financial Data", "dork": 'site:{domain} (intext:"bank account" OR intext:"routing number" OR intext:"iban" OR intext:"swift")', "desc": "Find financial data"},
                {"name": "Salary Info", "dork": 'site:{domain} (filetype:xls OR filetype:xlsx OR filetype:csv) (salary OR payroll OR compensation)', "desc": "Find salary info"},
                {"name": "Customer Data", "dork": 'site:{domain} (filetype:csv OR filetype:xls) (customer OR client OR user) (email OR phone OR address)', "desc": "Find customer data"},
                {"name": "Internal Docs", "dork": 'site:{domain} (intitle:"confidential" OR intitle:"internal" OR intitle:"private" OR intitle:"restricted")', "desc": "Find internal docs"},
                {"name": "Board Minutes", "dork": 'site:{domain} (filetype:pdf OR filetype:doc) (minutes OR meeting OR board) confidential', "desc": "Find board minutes"},
                {"name": "Contracts", "dork": 'site:{domain} (filetype:pdf OR filetype:doc) (contract OR agreement OR nda OR "non-disclosure")', "desc": "Find contracts"},
            ],
            "🌍 Network & IoT Devices": [
                {"name": "Webcams", "dork": 'site:{domain} (intitle:"webcam" OR intitle:"camera" OR intitle:"live view" OR inurl:viewer OR inurl:view/view.shtml)', "desc": "Find webcams"},
                {"name": "Network Devices", "dork": 'site:{domain} (intitle:"router" OR intitle:"switch" OR intitle:"firewall" OR intitle:"access point")', "desc": "Find network devices"},
                {"name": "Printers", "dork": 'site:{domain} (intitle:"printer" OR intitle:"print server" OR inurl:hp/device OR inurl:printer/main)', "desc": "Find printers"},
                {"name": "NAS/Storage", "dork": 'site:{domain} (intitle:"nas" OR intitle:"synology" OR intitle:"qnap" OR intitle:"storage")', "desc": "Find NAS devices"},
                {"name": "SCADA/ICS", "dork": 'site:{domain} (intitle:"scada" OR intitle:"hmi" OR intitle:"plc" OR intitle:"industrial")', "desc": "Find SCADA/ICS systems"},
                {"name": "VoIP Systems", "dork": 'site:{domain} (intitle:"voip" OR intitle:"asterisk" OR intitle:"pbx" OR intitle:"cisco" inurl:phone)', "desc": "Find VoIP systems"},
                {"name": "UPS/Power", "dork": 'site:{domain} (intitle:"ups" OR intitle:"apc" OR intitle:"power management")', "desc": "Find UPS systems"},
                {"name": "Building Systems", "dork": 'site:{domain} (intitle:"hvac" OR intitle:"building management" OR intitle:"bms" OR intitle:"automation")', "desc": "Find building systems"},
            ],
            "📱 Mobile & Apps": [
                {"name": "Android APK", "dork": 'site:{domain} filetype:apk', "desc": "Find Android apps"},
                {"name": "iOS IPA", "dork": 'site:{domain} filetype:ipa', "desc": "Find iOS apps"},
                {"name": "Mobile Config", "dork": 'site:{domain} filetype:mobileconfig', "desc": "Find mobile configs"},
                {"name": "App Store", "dork": 'site:apps.apple.com "{company}"', "desc": "Find iOS apps"},
                {"name": "Google Play", "dork": 'site:play.google.com "{company}"', "desc": "Find Android apps"},
                {"name": "Mobile API", "dork": 'site:{domain} (inurl:mobile OR inurl:app) (inurl:api OR inurl:rest OR inurl:json)', "desc": "Find mobile APIs"},
                {"name": "plist Files", "dork": 'site:{domain} filetype:plist', "desc": "Find iOS plist files"},
            ],
        }
    }

def load_dorks():
    try:
        with open('dorks.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        dorks = get_default_dorks()
        with open('dorks.json', 'w') as f:
            json.dump(dorks, f, indent=2)
        return dorks

def save_dorks(dorks):
    with open('dorks.json', 'w') as f:
        json.dump(dorks, f, indent=2)

def generate_search_url(dork, target, search_engine='google', custom_query=''):
    if '{custom}' in dork:
        query = custom_query
    else:
        domain = re.sub(r'^https?://', '', target)
        domain = re.sub(r'/.*$', '', domain)
        domain = domain.strip()
        
        company = target.replace('.com', '').replace('.org', '').replace('.net', '')
        company = re.sub(r'^www\.', '', company)
        
        query = dork.format(domain=domain, company=company, custom=custom_query)
    
    encoded_query = urllib.parse.quote(query)
    
    search_urls = {
        'google': f'https://www.google.com/search?q={encoded_query}',
        'bing': f'https://www.bing.com/search?q={encoded_query}',
        'duckduckgo': f'https://duckduckgo.com/?q={encoded_query}',
        'yahoo': f'https://search.yahoo.com/search?p={encoded_query}',
        'yandex': f'https://yandex.com/search/?text={encoded_query}',
        'baidu': f'https://www.baidu.com/s?wd={encoded_query}',
    }
    
    return {
        'query': query,
        'url': search_urls.get(search_engine, search_urls['google']),
        'encoded': encoded_query
    }

@app.route('/')
def index():
    dorks = load_dorks()
    return render_template('index.html', dorks=dorks)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    target = data.get('target', '')
    selected_dorks = data.get('dorks', [])
    search_engine = data.get('search_engine', 'google')
    custom_query = data.get('custom_query', '')
    
    results = []
    dorks_data = load_dorks()
    
    if custom_query and custom_query.strip():
        search_info = generate_search_url('{custom}', target, search_engine, custom_query)
        results.append({
            'category': '🔍 Custom Search',
            'name': 'Custom Dork',
            'query': search_info['query'],
            'url': search_info['url'],
            'dork': custom_query
        })
    
    for category_name, dorks_list in dorks_data['categories'].items():
        for dork_item in dorks_list:
            if dork_item['name'] in selected_dorks:
                search_info = generate_search_url(
                    dork_item['dork'], 
                    target, 
                    search_engine,
                    custom_query
                )
                results.append({
                    'category': category_name,
                    'name': dork_item['name'],
                    'query': search_info['query'],
                    'url': search_info['url'],
                    'dork': dork_item['dork'],
                    'description': dork_item.get('desc', '')
                })
    
    return jsonify({
        'success': True,
        'results': results,
        'count': len(results),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/dorks')
def get_dorks():
    return jsonify(load_dorks())

@app.route('/export/txt', methods=['POST'])
def export_txt():
    data = request.get_json()
    results = data.get('results', [])
    
    output = "=" * 60 + "\n"
    output += "    OSINT DORK LINKS EXPORT\n"
    output += "    Advanced Footprinting Tool\n"
    output += "=" * 60 + "\n"
    output += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    output += f"Total Dorks: {len(results)}\n"
    output += "=" * 60 + "\n\n"
    
    current_category = ""
    for result in results:
        if result['category'] != current_category:
            current_category = result['category']
            output += f"\n{'='*60}\n"
            output += f" {current_category}\n"
            output += f"{'='*60}\n\n"
        
        output += f"[{result['name']}]\n"
        output += f"Query: {result['query']}\n"
        output += f"URL: {result['url']}\n"
        output += "-" * 40 + "\n\n"
    
    return jsonify({
        'content': output, 
        'filename': f'osint-dorks-{datetime.now().strftime("%Y%m%d-%H%M%S")}.txt'
    })

@app.route('/export/html', methods=['POST'])
def export_html():
    data = request.get_json()
    results = data.get('results', [])
    target = data.get('target', 'Unknown')
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>OSINT Report - {target}</title>
    <style>
        body {{ font-family: 'Courier New', monospace; background: #c0c0c0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: #fff; border: 2px outset #fff; padding: 20px; }}
        h1 {{ color: #000080; border-bottom: 2px solid #000080; }}
        .result {{ background: #efefef; border: 1px inset #808080; padding: 10px; margin: 10px 0; }}
        .category {{ color: #800000; font-weight: bold; }}
        a {{ color: #0000ff; }}
        .query {{ background: #000; color: #0f0; padding: 5px; font-family: monospace; word-break: break-all; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 OSINT Dork Report</h1>
        <p><strong>Target:</strong> {target}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Total Results:</strong> {len(results)}</p>
        <hr>
"""
    
    for result in results:
        html += f"""
        <div class="result">
            <div class="category">{result['category']}</div>
            <strong>{result['name']}</strong>
            <div class="query">{result['query']}</div>
            <a href="{result['url']}" target="_blank">🔗 Open Search</a>
        </div>
"""
    
    html += """
    </div>
</body>
</html>"""
    
    return jsonify({
        'content': html,
        'filename': f'osint-report-{datetime.now().strftime("%Y%m%d-%H%M%S")}.html'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)