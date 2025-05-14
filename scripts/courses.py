import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Base URL for relative links
base_url = 'https://www.southflorida.edu'
academics_url = 'https://www.southflorida.edu/current-students/degrees-programs/academics'

# HTML snippet provided
html_snippet = '''
<div class="col-md-3 col-sm-4">
          <div class="sideNav">
            <ul class="sidebarMenu"><li class="page_item page-item-10430 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/associate-arts-aa">Associate in Arts – AA</a>
<ul class="children">
	<li class="page_item page-item-5097"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/associate-arts-aa/education-aa">Associate in Arts Degree</a></li>
	<li class="page_item page-item-23184 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/associate-arts-aa/arts-and-sciences-departments">Arts and Sciences Departments</a></li>
	<li class="page_item page-item-31991 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/associate-arts-aa/degree-maps-major">Degree Maps by Major</a></li>
	<li class="page_item page-item-31353"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/associate-arts-aa/usf-fuse">USF FUSE Transfer Program</a></li>
</ul>
</li>
<li class="page_item page-item-5080 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/accounting">Accounting</a>
<ul class="children">
	<li class="page_item page-item-5181"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/accounting/accounting-technology-1580">Accounting Technology – AS</a></li>
	<li class="page_item page-item-5180"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/accounting/accounting-applications-3010">Accounting Applications – CCC</a></li>
</ul>
</li>
<li class="page_item page-item-5204 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/automotive-programs">Automotive</a>
<ul class="children">
	<li class="page_item page-item-5207"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/automotive-programs/service-technology-3220">Auto Service Technology – CC</a></li>
	<li class="page_item page-item-5205"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/automotive-programs/collision-technology-technician-3210">Auto Collision Technology Technician – CC</a></li>
</ul>
</li>
<li class="page_item page-item-5083 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/business">Business</a>
<ul class="children">
	<li class="page_item page-item-5086 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/business/supervision-management-bas">Bachelor of Applied Science in Supervision and Management (BAS-SM)</a></li>
	<li class="page_item page-item-5084"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/business/business-administration-as">Business Administration – AS</a></li>
	<li class="page_item page-item-5085"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/business/business-management-ccc">Business Management – CCC</a></li>
</ul>
</li>
<li class="page_item page-item-5211 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/cosmetology-programs">Cosmetology</a>
<ul class="children">
	<li class="page_item page-item-5212"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/cosmetology-programs/cosmetology-3280">Cosmetology – CC</a></li>
</ul>
</li>
<li class="page_item page-item-10510 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/public-safety">Criminal Justice Academy</a>
<ul class="children">
	<li class="page_item page-item-10512"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/public-safety/criminal-justice-technology">Criminal Justice Technology – AS</a></li>
	<li class="page_item page-item-16877"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/public-safety/training-calendar-corrections-law-enforcement">Criminal Justice Training Calendar</a></li>
	<li class="page_item page-item-10526"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/public-safety/law-enforcement-auxiliary-officer-cc">Law Enforcement Auxiliary Officer – CC</a></li>
	<li class="page_item page-item-10528"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/public-safety/law-enforcement-correctional-crossover-cc">Law Enforcement to Correctional – CC</a></li>
	<li class="page_item page-item-10523"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/public-safety/fl-law-enforcement-academy">Florida Law Enforcement Academy- CC</a></li>
	<li class="page_item page-item-10514 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/public-safety/correctional-officer-cc">Correctional Officer – CC</a></li>
	<li class="page_item page-item-36260"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/public-safety/3352-public-safety-communication">Public Safety Communication – CC</a></li>
	<li class="page_item page-item-63201"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/public-safety/bas-sm-with-criminal-justice-specialization">BAS-SM with Criminal Justice Specialization</a></li>
</ul>
</li>
<li class="page_item page-item-62926"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/drafting">Drafting</a></li>
<li class="page_item page-item-41079 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/elementary-education-bs">Elementary Teacher Education – BS</a>
<ul class="children">
	<li class="page_item page-item-41130"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/elementary-education-bs/bsete-admission-requirements">BSETE Admission Requirements</a></li>
	<li class="page_item page-item-41178"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/elementary-education-bs/bsete-general-student-information">BSETE General Student Information</a></li>
	<li class="page_item page-item-41177"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/elementary-education-bs/bsete-program-plan-2">BSETE Program Plan</a></li>
	<li class="page_item page-item-41179"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/elementary-education-bs/bsete-internshipstudent-teaching">BSETE Internship/Student Teaching</a></li>
	<li class="page_item page-item-25300"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/elementary-education-bs/resources">BSETE Student Resources</a></li>
	<li class="page_item page-item-25258"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/elementary-education-bs/contacts">BSETE Program Contacts</a></li>
	<li class="page_item page-item-26826"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/elementary-education-bs/education-scholarships-and-grants">Education Scholarships and Grants</a></li>
	<li class="page_item page-item-60387"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/elementary-education-bs/bsete-site-visit">BSETE Site Visit</a></li>
	<li class="page_item page-item-63983"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/elementary-education-bs/state-exam-test-study-materials">State Exam Test Study Materials</a></li>
</ul>
</li>
<li class="page_item page-item-5213 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/electrical-programs">Electricity</a>
<ul class="children">
	<li class="page_item page-item-11114"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/electrical-programs/electrical-app">Electrical Apprenticeship Program</a></li>
	<li class="page_item page-item-5214"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/electrical-programs/electrical-lineworker-cc">Electrical Lineworker – CC</a></li>
</ul>
</li>
<li class="page_item page-item-5215 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/electronics">Electronics</a>
<ul class="children">
	<li class="page_item page-item-65164"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/electronics/computer-systems-information-technology">Computer Systems Information Technology</a></li>
	<li class="page_item page-item-10484"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/electronics/biomedical-equipment-tech">Biomedical Equipment Technician – AS</a></li>
	<li class="page_item page-item-5217"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/electronics/computer-engineering-technology-1680">Computer Engineering Technology – AS</a></li>
</ul>
</li>
<li class="page_item page-item-5065 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/emergency-medical-services">Emergency Medical Services</a>
<ul class="children">
	<li class="page_item page-item-5190"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/emergency-medical-services/emergency-medical-services-1660">Emergency Medical Services – AS</a></li>
	<li class="page_item page-item-5191 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/emergency-medical-services/emergency-medical-technician-basic-2810">Emergency Medical Technician (Basic)</a></li>
	<li class="page_item page-item-5195 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/emergency-medical-services/paramedic-3042">Paramedic – CCC</a></li>
	<li class="page_item page-item-12185"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/emergency-medical-services/ems-contacts">EMS Contacts</a></li>
</ul>
</li>
<li class="page_item page-item-20484 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/fire-science">Fire Science</a>
<ul class="children">
	<li class="page_item page-item-5231"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/fire-science/fire-science-technology-1670">Fire Science Technology – AS</a></li>
	<li class="page_item page-item-20496"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/fire-science/firefighter-minimum-standards">Minimum Standards Application Process</a></li>
	<li class="page_item page-item-20760"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/fire-science/faqs">Fire Science FAQs</a></li>
	<li class="page_item page-item-20498"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/fire-science/fire-science-contacts">Fire Science Contacts</a></li>
</ul>
</li>
<li class="page_item page-item-39947 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/health-sciences">Health Sciences</a>
<ul class="children">
	<li class="page_item page-item-44645"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/health-sciences/health-services">Health Services</a></li>
	<li class="page_item page-item-5091"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/health-sciences/medical-administrative-specialist">Medical Administrative Specialist – CC</a></li>
	<li class="page_item page-item-40107 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/health-sciences/dental">Dental</a></li>
	<li class="page_item page-item-39885 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/health-sciences/nursing">Nursing</a></li>
	<li class="page_item page-item-39376"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/health-sciences/phlebotomy">Phlebotomy – CC</a></li>
	<li class="page_item page-item-39653 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/health-sciences/radiography-as">Radiography – AS</a></li>
	<li class="page_item page-item-55562 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/health-sciences/surgical-services">Surgical Services</a></li>
	<li class="page_item page-item-41149"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/health-sciences/conference-on-caring">Conference on Caring</a></li>
	<li class="page_item page-item-19634"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/health-sciences/fingerprinting-background-check">Fingerprinting Background Check</a></li>
	<li class="page_item page-item-59341"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/health-sciences/advanced-patient-care-tech-apprenticeship">Advanced Patient Care Tech Apprenticeship</a></li>
</ul>
</li>
<li class="page_item page-item-5117 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/hvacr">Heating, Ventilation, Air-Conditioning/Refrigeration (HVAC/R)</a>
<ul class="children">
	<li class="page_item page-item-5233"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/hvacr/hvacr-cc">Heating, Ventilation, Air Conditioning/Refrigeration (HVAC/R) – CC</a></li>
	<li class="page_item page-item-5119"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/hvacr/commercial-air-conditioning-app">Commercial Air Conditioning – APP</a></li>
</ul>
</li>
<li class="page_item page-item-10490 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/honors-program">Honors Program</a>
<ul class="children">
	<li class="page_item page-item-13201"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/honors-program/application">Application</a></li>
	<li class="page_item page-item-24901"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/honors-program/admission-requirements">Admission/Graduation Requirements</a></li>
	<li class="page_item page-item-13204"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/honors-program/courses">Courses</a></li>
	<li class="page_item page-item-13210"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/honors-program/scholarships">Honors Scholarships</a></li>
	<li class="page_item page-item-24906"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/honors-program/service-learning">Service Learning</a></li>
	<li class="page_item page-item-13206"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/honors-program/faculty">Faculty</a></li>
</ul>
</li>
<li class="page_item page-item-5087 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/hospitality">Hospitality</a>
<ul class="children">
	<li class="page_item page-item-5088"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/hospitality/professional-culinary-arts-and-hospitality">Professional Culinary Arts and Hospitality – CC</a></li>
</ul>
</li>
<li class="page_item page-item-41040"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/industrial-management-technology">Industrial Management Technology – AS</a></li>
<li class="page_item page-item-5232 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/information-technology">Information Technology</a>
<ul class="children">
	<li class="page_item page-item-5236"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/information-technology/computer-programming-analysis-1610">Computer Programming and Analysis – AS</a></li>
	<li class="page_item page-item-66619"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/information-technology/network-systems-technology-2">Network Systems Technology – AS</a></li>
	<li class="page_item page-item-5235"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/information-technology/computer-programming-3020">Computer Programming – CCC</a></li>
	<li class="page_item page-item-10466"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/information-technology/network-security-ccc">Network Security – CCC</a></li>
</ul>
</li>
<li class="page_item page-item-32054 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/mechatronics">Mechatronics</a>
<ul class="children">
	<li class="page_item page-item-54557"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/mechatronics/advanced-manufacturing-and-production-technology-cc">Advanced Manufacturing and Production Technology – CC</a></li>
	<li class="page_item page-item-33530"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/mechatronics/engineering-technology-as">Engineering Technology – AS</a></li>
	<li class="page_item page-item-54622"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/mechatronics/pneumatics-hydraulics-and-motors-for-manufacturing-ccc">Pneumatics, Hydraulics, and Motors for Manufacturing – CCC</a></li>
	<li class="page_item page-item-33542"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/mechatronics/mechatronics-college-credit-certiticates">Mechatronics College Credit Certificates</a></li>
	<li class="page_item page-item-32102"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/mechatronics/mechatronics-contacts">Mechatronics Contacts</a></li>
</ul>
</li>
<li class="page_item page-item-5089 page_item_has_children"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/office-administration-management">Office Administration and Management</a>
<ul class="children">
	<li class="page_item page-item-5094"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/office-administration-management/office-management-ccc">Office Management – CCC</a></li>
	<li class="page_item page-item-5090"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/office-administration-management/administrative-office-specialist-cc">Administrative Office Specialist – CC</a></li>
	<li class="page_item page-item-5093"><a href="https://www.southflorida.edu/current-students/degrees-programs/academics/office-administration-management/office-administration-as">Office Administration – AS</a></li>
</ul>
</li>
</ul>
            <script>
              $(document).ready(function () {
                $('.sideNav > .pagenav >  ul').addClass('sidebarMenu');
                $('.sidebarMenu').detach().insertBefore('.sideNavInsert');
                $('.sideNav > .pagenav').remove();
                $('.sideNavInsert').remove();
              });
            </script>
          </div>
        </div>
'''

# List to store program data
programs = []

# Function to extract programs recursively
def extract_programs(ul_element, parent_name=None):
    for li in ul_element.find_all('li', recursive=False):
        a_tag = li.find('a', href=True)
        if not a_tag:
            continue
        program_name = a_tag.get_text(strip=True)
        program_url = urljoin(base_url, a_tag['href'])
        
        programs.append({
            'Name': program_name,
            'URL': program_url,
            'Parent': parent_name if parent_name else 'N/A'
        })
        logging.info(f"Extracted: {program_name}")
        
        # Process nested subprograms
        children_ul = li.find('ul', class_='children')
        if children_ul:
            extract_programs(children_ul, program_name)

# Function to process the snippet
def process_snippet():
    try:
        soup = BeautifulSoup(html_snippet, 'html.parser')
        
        # Find sidebar menu
        sidebar = soup.find('div', class_='sideNav')
        if not sidebar:
            logging.error("Error: No sidebar found")
            return False
        
        program_list = sidebar.find('ul', class_='sidebarMenu')
        if not program_list:
            logging.error("Error: No program list found")
            return False
        
        extract_programs(program_list)
        return True
    
    except Exception as e:
        logging.error(f"Error parsing snippet: {e}")
        return False

# Run extraction
if __name__ == '__main__':
    success = process_snippet()
    
    # Save to CSV
    if programs:
        df = pd.DataFrame(programs)
        df.to_csv('sfsc_programs.csv', index=False)
        logging.info(f"Success! Saved {len(programs)} programs to sfsc_programs.csv")
    else:
        logging.info("Error: No data extracted. The list may be malformed or missing.")