# import streamlit as st
# import boto3
# import pandas as pd
# import json
# import requests
# import math
# from datetime import date
# import plotly.express as px

# # === Page Configuration ===
# st.set_page_config(
#     page_title="Lonestar Real Estate - Property Manager",
#     page_icon="🏠",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # === AWS Configuration ===
# @st.cache_resource
# def init_s3_client():
#     return boto3.client(
#         's3',
#         region_name='us-east-1',
#         aws_access_key_id=st.secrets.get("AWS_ACCESS_KEY_ID", "your_access_key"),
#         aws_secret_access_key=st.secrets.get("AWS_SECRET_ACCESS_KEY", "your_secret_key")
#     )

# # === S3 Operations ===
# def download_from_s3(s3_client, bucket_name, file_key):
#     """Download existing JSON file from S3"""
#     try:
#         obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
#         raw_data = obj['Body'].read()
#         data = json.loads(raw_data)
#         return data
#     except s3_client.exceptions.NoSuchKey:
#         return []
#     except Exception as e:
#         st.error(f"Error reading {file_key}: {e}")
#         return []

# def upload_to_s3(s3_client, bucket_name, file_key, data):
#     """Upload updated JSON back to S3"""
#     try:
#         s3_client.put_object(
#             Bucket=bucket_name,
#             Key=file_key,
#             Body=json.dumps(data, indent=2).encode('utf-8'),
#             ContentType='application/json'
#         )
#         return True
#     except Exception as e:
#         st.error(f"Error uploading {file_key}: {e}")
#         return False

# # === LocationIQ Integration ===
# def get_coordinates(address, api_key):
#     """Get coordinates from LocationIQ API"""
#     if not api_key:
#         st.error("LocationIQ API key not configured")
#         return None, None
    
#     try:
#         params = {
#             'key': api_key,
#             'q': address,
#             'format': 'json',
#             'limit': 1
#         }
        
#         response = requests.get('https://us1.locationiq.com/v1/search.php', params=params)
        
#         if response.status_code == 200:
#             data = response.json()
#             if data:
#                 lat = float(data[0]['lat'])
#                 lon = float(data[0]['lon'])
#                 return lat, lon
#             else:
#                 st.error("No coordinates found for this address")
#                 return None, None
#         else:
#             st.error(f"LocationIQ API error: {response.status_code}")
#             return None, None
            
#     except Exception as e:
#         st.error(f"Error fetching coordinates: {e}")
#         return None, None

# # === Distance Calculation ===
# def calculate_distance(lat1, lon1, lat2, lon2):
#     """Calculate distance using Haversine formula"""
#     R = 3959  # Earth's radius in miles
    
#     lat1_rad = math.radians(lat1)
#     lon1_rad = math.radians(lon1)
#     lat2_rad = math.radians(lat2)
#     lon2_rad = math.radians(lon2)
    
#     dlat = lat2_rad - lat1_rad
#     dlon = lon2_rad - lon1_rad
    
#     a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
#     distance = R * c
    
#     return round(distance, 2)

# # === Ideal Comp Filtering ===
# def find_ideal_comps(candidate, comps, max_distance=None):
#     """Find ideal comps based on size, year built, and distance criteria"""
#     ideal_comps = []
    
#     candidate_size = candidate.get('Size (sqft)', 0)
#     candidate_year = candidate.get('Year Built', None)
#     candidate_price = candidate.get('Price', 0)
#     candidate_lat = candidate.get('Latitude')
#     candidate_lon = candidate.get('Longitude')
    
#     for comp in comps:
#         comp_size = comp.get('Size (sqft)', 0)
#         comp_year = comp.get('Year Built', None)
#         comp_price = comp.get('Price', 0)
#         comp_lat = comp.get('Latitude')
#         comp_lon = comp.get('Longitude')
        
#         # Size criteria: ±1000 sqft
#         size_match = abs(comp_size - candidate_size) <= 250
        
#         # Year built criteria: ±25 years (if both have year built)
#         year_match = True  # Default to True if either doesn't have year
#         if candidate_year and comp_year:
#             year_match = abs(comp_year - candidate_year) <= 15

#         price_match = True  # Default to True if either doesn't have year
#         if candidate_price and comp_price:
#             price_match = (comp_price - candidate_price) >= 50000     
        
#         # Distance criteria (if specified)
#         distance_match = True
#         distance = None
#         if max_distance and candidate_lat and candidate_lon and comp_lat and comp_lon:
#             distance = calculate_distance(candidate_lat, candidate_lon, comp_lat, comp_lon)
#             distance_match = distance <= max_distance
        
#         if size_match and year_match and distance_match and price_match:
#             comp_with_distance = comp.copy()
#             if distance is not None:
#                 comp_with_distance['Distance'] = distance
#             elif candidate_lat and candidate_lon and comp_lat and comp_lon:
#                 comp_with_distance['Distance'] = calculate_distance(candidate_lat, candidate_lon, comp_lat, comp_lon)
#             ideal_comps.append(comp_with_distance)
    
#     return ideal_comps


# # === Property Table Display ===
# def display_properties_table(properties, property_type):
#     """Display properties in a compact table format with metrics"""
#     if not properties:
#         st.info(f"No {property_type} properties found.")
#         return
    
#     # Calculate and display metrics
#     df_raw = pd.DataFrame(properties)
    
#     # Metrics row
#     col1, col2, col3, col4 = st.columns(4)
#     with col1:
#         avg_price = df_raw['Price'].mean()
#         st.metric("Avg Price", f"${avg_price:,.0f}")
#     with col2:
#         avg_size = df_raw['Size (sqft)'].mean()
#         st.metric("Avg Size", f"{avg_size:,.0f} sqft")
#     with col3:
#         avg_price_sqft = df_raw['Price/SqFt'].mean()
#         st.metric("Avg Price/SqFt", f"${avg_price_sqft:.0f}")
#     with col4:
#         total_count = len(df_raw)
#         st.metric("Total Properties", total_count)
    
#     # Convert to display format - showing ALL columns
#     df_data = []
#     for prop in properties:
#         row = {}
#         # Add all available fields
#         for key, value in prop.items():
#             if key == 'Price':
#                 row[key] = f"${value:,}"
#             elif key == 'Size (sqft)':
#                 row[key] = f"{value:,}"
#             elif key == 'Price/SqFt':
#                 row[key] = f"${value:.0f}"
#             elif isinstance(value, (int, float)) and key not in ['Latitude', 'Longitude']:
#                 row[key] = f"{value:,}" if value > 1000 else str(value)
#             else:
#                 row[key] = str(value) if value is not None else ''
#         df_data.append(row)
    
#     df = pd.DataFrame(df_data)
    
#     # Display with clickable links
#     st.dataframe(
#         df,
#         use_container_width=True,
#         column_config={
#             "URL": st.column_config.LinkColumn(
#                 "View Listing",
#                 help="Click to view property listing",
#                 validate="^https://.*",
#                 max_chars=100,
#                 display_text="🔗 View"
#             ),
#             "Address": st.column_config.TextColumn(
#                 "Address",
#                 width="large"
#             ),
#             "Size (sqft)": st.column_config.TextColumn(
#                 "Size (sqft)",
#                 width="small"
#             ),
#             "Price": st.column_config.TextColumn(
#                 "Price",
#                 width="medium"
#             ),
#             "Price/SqFt": st.column_config.TextColumn(
#                 "Price/SqFt",
#                 width="small"
#             )
#         },
#         hide_index=True
#     )



# # === Filter Functions ===
# def filter_comps(comps, candidate, price_min=None, price_max=None, size_min=None, size_max=None, 
#                  year_min=None, year_max=None, max_distance=None):
#     """Filter comps based on criteria and calculate distances"""
#     filtered = []
    
#     candidate_lat = candidate.get('Latitude')
#     candidate_lon = candidate.get('Longitude')
    
#     for comp in comps:
#         # Apply price filter
#         if price_min is not None and comp.get('Price', 0) < price_min:
#             continue
#         if price_max is not None and comp.get('Price', 0) > price_max:
#             continue
            
#         # Apply size filter
#         if size_min is not None and comp.get('Size (sqft)', 0) < size_min:
#             continue
#         if size_max is not None and comp.get('Size (sqft)', 0) > size_max:
#             continue
            
#         # Apply year filter
#         if year_min is not None and (not comp.get('Year Built') or comp.get('Year Built') < year_min):
#             continue
#         if year_max is not None and (not comp.get('Year Built') or comp.get('Year Built') > year_max):
#             continue
        
#         # Calculate distance and apply distance filter
#         comp_lat = comp.get('Latitude')
#         comp_lon = comp.get('Longitude')
        
#         if candidate_lat and candidate_lon and comp_lat and comp_lon:
#             distance = calculate_distance(candidate_lat, candidate_lon, comp_lat, comp_lon)
#             if max_distance is not None and distance > max_distance:
#                 continue
            
#             # Add distance to comp data
#             comp_with_distance = comp.copy()
#             comp_with_distance['Distance'] = distance
#             filtered.append(comp_with_distance)
#         else:
#             # If no coordinates, include if no distance filter
#             if max_distance is None:
#                 filtered.append(comp)
    
#     return filtered

# APP_ID = st.secrets.get("PODIO_APP_ID")
# APP_TOKEN = st.secrets.get("PODIO_APP_TOKEN")
# CLIENT_ID = st.secrets.get("PODIO_CLIENT_ID")
# CLIENT_SECRET = st.secrets.get("PODIO_CLIENT_SECRET")

# # Step 1: Authenticate and get access token
# def get_access_token():
#     try:
#         import requests
#         response = requests.post(
#             "https://podio.com/oauth/token",
#             data={
#                 "grant_type": "app",
#                 "app_id": APP_ID,
#                 "app_token": APP_TOKEN,
#                 "client_id": CLIENT_ID,
#                 "client_secret": CLIENT_SECRET
#             }
#         )
#         return response.json()["access_token"]
#     except Exception as e:
#         st.error(f"Error getting access token: {str(e)}")
#         return None

# # Helper function to convert date to Podio datetime format
# def convertToPodioDatetime(date_string):
#     """Convert date string to Podio datetime format"""
#     try:
#         from datetime import datetime
#         if date_string:
#             # Adjust this based on your date format
#             dt = datetime.strptime(str(date_string), "%Y-%m-%d")
#             return dt.strftime("%Y-%m-%d %H:%M:%S")
#         return None
#     except:
#         return None

# # Step 2: Post item to Podio app
# def send_to_podio(data):
#     try:
#         import requests
#         access_token = get_access_token()
#         if not access_token:
#             return False, "Failed to get access token"
            
#         url = f"https://api.podio.com/item/app/{APP_ID}/"
#         headers = {
#             "Authorization": f"OAuth2 {access_token}",
#             "Content-Type": "application/json"
#         }
        
#         # Build payload with only non-empty fields
#         fields = {}
        
#         # Address - required field, must have value
#         if data.get('Address'):
#             fields["address"] = data.get('Address', '')
        
#         # Price - only add if has valid value
#         if data.get('Price') and data.get('Price') > 0:
#             fields["listing-price"] = {
#                 "value": data.get('Price', 0),
#                 "currency": "USD"
#             }
        
#         # Listing date - only add if has valid date
#         listing_date = data.get("Listing Date") or data.get("Sold Date") or data.get("Snapshot Date")
#         if listing_date and str(listing_date).strip():
#             formatted_date = convertToPodioDatetime(listing_date)
#             if formatted_date:
#                 fields["listing-date"] = {
#                     "start": formatted_date,
#                     "end": formatted_date
#                 }
        
#         # Agent name - only add if has value
#         if data.get("Agent Name") and str(data.get("Agent Name")).strip():
#             fields["agent-name"] = data.get("Agent Name", "")
        
#         # Square feet - only add if has valid value
#         if data.get("Size (sqft)") and data.get("Size (sqft)") > 0:
#             fields["square-feet"] = str(data.get("Size (sqft)", ""))
        
#         # Format final payload
#         payload = {"fields": fields}
        
#         # Debug: print payload to see what's being sent
#         # st.write("Debug - Payload being sent to Podio:", payload)
        
#         res = requests.post(url, json=payload, headers=headers)
        
#         if res.status_code == 200:
#             return True, "Successfully sent to Podio!"
#         else:
#             return False, f"Failed to send to Podio: {res.status_code} - {res.text}"
            
#     except ImportError:
#         return False, "Please install 'requests' library: pip install requests"
#     except Exception as e:
#         return False, f"Error sending to Podio: {str(e)}"


# # === Main App ===
# def main():
#     # Initialize session state very early and make it persistent  
#     if 'logged_in' not in st.session_state:
#         st.session_state.logged_in = False
#     if 'username' not in st.session_state:
#         st.session_state.username = None
#     if 'selected_candidate_idx' not in st.session_state:
#         st.session_state.selected_candidate_idx = None
    
#     # Persistent filters - use underscore prefix for widget keys
#     if 'enable_distance_filter' not in st.session_state:
#         st.session_state.enable_distance_filter = True
#     if 'enable_price_filter' not in st.session_state:
#         st.session_state.enable_price_filter = False
#     if 'enable_size_filter' not in st.session_state:
#         st.session_state.enable_size_filter = False  
#     if 'enable_year_filter' not in st.session_state:
#         st.session_state.enable_year_filter = False
#     if 'max_distance' not in st.session_state:
#         st.session_state.max_distance = 10.0
#     if 'price_range' not in st.session_state:
#         st.session_state.price_range = (50000, 1000000)
#     if 'size_range' not in st.session_state:
#         st.session_state.size_range = (800, 4000)
#     if 'year_range' not in st.session_state:
#         st.session_state.year_range = (1980, 2020)
    
#     st.title("🏠 Lonestar Real Estate - Property Manager")
#     st.markdown("Add candidate and comp properties with automatic coordinate enrichment and distance analysis.")
    
#     # Configuration - Updated for folder structure
#     bucket_name = lonestar-realestate-test # 'shinka-realestate-gold' # 'lonestar-realestate-test' # 
#     candidate_file = 'candidate/candidate.json'
#     comp_file = 'comps/comp.json'
    
#     # Initialize S3 client
#     s3_client = init_s3_client()
    
#     # Sidebar Configuration
#     st.sidebar.header("⚙️ Configuration")
    
#     # Show login status in sidebar
#     if st.session_state.logged_in:
#         st.sidebar.success(f"✅ Logged in as: {st.session_state.username}")
#         if st.sidebar.button("🚪 Logout"):
#             # Clear all session state on logout
#             for key in list(st.session_state.keys()):
#                 del st.session_state[key]
#             st.rerun()
#     else:
#         st.sidebar.warning("🔒 Not logged in")
    
#     # Get API key from secrets (don't show input to user)
#     locationiq_api_key = st.secrets.get("LOCATIONIQ_API_KEY", "")
    
#     # Load existing data
#     if st.sidebar.button("🔄 Refresh Data from S3"):
#         st.cache_data.clear()
    
#     @st.cache_data(ttl=60)
#     def load_data():
#         candidates = download_from_s3(s3_client, bucket_name, candidate_file)
#         comps = download_from_s3(s3_client, bucket_name, comp_file)
#         return candidates, comps
    
#     candidates, comps = load_data()

#     # Main content tabs - always show tabs but control content
#     tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔐 Login", "📝 Add Property", "🏠 Candidates", "📊 Comps", "📏 Distance Analysis"])
    
#     # === TAB 1: Login ===
#     with tab1:
#         st.header("🔐 User Login")
        
#         # Check if already logged in and show logout option
#         if st.session_state.logged_in:
#             st.success(f"✅ Currently logged in as: **{st.session_state.username}**")
#             st.info("You can now access all features of the application. Use the other tabs to manage properties.")
            
#             col1, col2 = st.columns([1, 3])
#             with col1:
#                 if st.button("🚪 Logout", type="secondary"):
#                     # Clear all session state on logout
#                     for key in list(st.session_state.keys()):
#                         del st.session_state[key]
#                     st.rerun()
#             with col2:
#                 st.markdown("### Quick Navigation")
#                 st.markdown("""
#                 - **📝 Add Property**: Add new candidate or comp properties
#                 - **🏠 Candidates**: View all candidate properties
#                 - **📊 Comps**: View all comparable properties  
#                 - **📏 Distance Analysis**: Analyze distances and find ideal comps
#                 """)
#         else:
#             # Show login form only if not logged in
#             with st.form("login_form"):
#                 col1, col2 = st.columns([1, 2])
                
#                 with col1:
#                     st.markdown("### Login Credentials")
#                     username = st.text_input("Username", placeholder="Enter your username")
#                     password = st.text_input("Password", type="password", placeholder="Enter your password")
                    
#                     login_submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
                    
#                     if login_submitted:
#                         if username and password:
#                             # Add your authentication logic here
#                             if username == "admin" and password == "password123":  # Example credentials
#                                 st.success("✅ Login successful!")
#                                 st.session_state.logged_in = True
#                                 st.session_state.username = username
#                                 st.rerun()
#                             else:
#                                 st.error("❌ Invalid username or password")
#                         else:
#                             st.error("Please enter both username and password")
                
#                 with col2:
#                     st.markdown("### System Information")
#                     st.info(
#                         "**Welcome to Lonestar Real Estate Property Manager**\n\n"
#                         "This system allows you to:\n"
#                         "- Add and manage candidate properties\n"
#                         "- Track comparable properties (comps)\n"
#                         "- Perform distance analysis\n"
#                         "- Send data to Podio CRM\n\n"
#                         "**Test Credentials:**\n"
#                         "- Username: admin\n"
#                         "- Password: password123"
#                     )
        
#         # IMPORTANT: Stop here - no more content should appear in this tab
#         # The property form you're seeing is a bug and should not be here

#     # Check if user is logged in before showing other tabs content
#     if not st.session_state.logged_in:
#         # Show message in other tabs if not logged in
#         with tab2:
#             st.warning("🔒 Please log in first to access this feature.")
#             st.info("Go to the Login tab to enter your credentials (admin/password123).")
        
#         with tab3:
#             st.warning("🔒 Please log in first to access this feature.")
#             st.info("Go to the Login tab to enter your credentials (admin/password123).")
        
#         with tab4:
#             st.warning("🔒 Please log in first to access this feature.")
#             st.info("Go to the Login tab to enter your credentials (admin/password123).")
        
#         with tab5:
#             st.warning("🔒 Please log in first to access this feature.")
#             st.info("Go to the Login tab to enter your credentials (admin/password123).")
    
#     else:
#         # User is logged in, show all functionality
#         # === TAB 2: Add Property ===
#         with tab2:
#             st.header("Add New Property")
            
#             # Property type selection outside the form
#             property_type = st.selectbox(
#                 "Property Type",
#                 options=["candidate", "comp"],
#                 format_func=lambda x: "Candidate" if x == "candidate" else "Comp",
#                 key="property_type_selector"
#             )
            
#             with st.form("property_form", clear_on_submit=True):
#                 col1, col2 = st.columns(2)
                
#                 with col1:
#                     address = st.text_input(
#                         "Address *",
#                         placeholder="e.g., 123 Main St, Houston, TX 77001",
#                         help="Enter the full property address (Required)"
#                     )
                    
#                     size_sqft = st.number_input(
#                         "Size (sq ft) *",
#                         min_value=1,
#                         value=None,
#                         placeholder="e.g., 2500"
#                     )
                    
#                     price = st.number_input(
#                         "Price ($) *",
#                         min_value=0,
#                         value=None,
#                         step=1000,
#                         placeholder="e.g., 350000"
#                     )
                    
#                     # Conditional date input based on property type
#                     if property_type == "candidate":
#                         listing_date = st.date_input(
#                             "Listing Date *",
#                             value=date.today(),
#                             help="Date when the property was listed"
#                         )
#                     else:
#                         sold_date = st.date_input(
#                             "Sold Date *",
#                             value=date.today(),
#                             help="Date when the property was sold"
#                         )
                
#                 with col2:
#                     bedrooms = st.number_input(
#                         "Bedrooms (optional)",
#                         min_value=0,
#                         max_value=20,
#                         value=None
#                     )
                    
#                     year_built = st.number_input(
#                         "Year Built (optional)",
#                         min_value=1800,
#                         max_value=2030,
#                         value=None
#                     )
#                     story = st.number_input(
#                         "Story (optional)",
#                         min_value=1,
#                         max_value=10,
#                         value=None,
#                         help="Number of stories/floors in the property"
#                     )                
#                     agent_name = st.text_input(
#                         "Agent Name (optional)",
#                         placeholder="e.g., John Smith"
#                     )
                    

                    
#                     # Auto-calculate price per sq ft
#                     if size_sqft and price:
#                         price_per_sqft = round(price / size_sqft, 2)
#                         st.metric("Price/SqFt (calculated)", f"${price_per_sqft}")
                
#                 # Submit button with dynamic text
#                 button_text = f"Add {property_type.title()}"
#                 submitted = st.form_submit_button(
#                     button_text, 
#                     type="primary",
#                     use_container_width=True
#                 )
                
#                 if submitted:
#                     # Check for mandatory fields
#                     missing_fields = []
#                     if not address or address.strip() == "":
#                         missing_fields.append("Address")
#                     if not size_sqft:
#                         missing_fields.append("Size (sq ft)")
#                     if not price:
#                         missing_fields.append("Price")
                    
#                     if missing_fields:
#                         st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")
#                     else:
#                         with st.spinner(f"Adding {property_type}..."):
#                             # Get coordinates
#                             lat, lon = get_coordinates(address.strip(), locationiq_api_key)
                            
#                             if lat is not None and lon is not None:
#                                 # Create property payload
#                                 new_property = {
#                                     "Address": address.strip(),
#                                     "Size (sqft)": size_sqft,
#                                     "Price": price,
#                                     "Price/SqFt": round(price / size_sqft, 2),
#                                     "Latitude": lat,
#                                     "Longitude": lon,
#                                     "Snapshot Date": str(date.today())
#                                 }
                                
#                                 # Add optional fields
#                                 if bedrooms:
#                                     new_property["Bedrooms"] = bedrooms
#                                 if year_built:
#                                     new_property["Year Built"] = year_built
#                                 if agent_name and agent_name.strip():
#                                     new_property["Agent Name"] = agent_name.strip()
#                                 if story:
#                                     new_property["Story"] = story
                                
#                                 # Add type-specific fields with user-provided dates
#                                 if property_type == "candidate":
#                                     new_property["Listing Date"] = str(listing_date)
#                                     new_property["URL"] = f"https://www.har.com/mapsearch?quicksearch={address.replace(' ', '+')}&view=map"
#                                 else:
#                                     new_property["Sold Date"] = str(sold_date)
#                                     new_property["URL"] = f"https://www.har.com/mapsearch?quicksearch={address.replace(' ', '+')}&view=map"
                                
#                                 # Add to existing data
#                                 if property_type == "candidate":
#                                     candidates_copy = candidates.copy()
#                                     st.write(f"before update row count: {len(candidates_copy)}")
#                                     candidates_copy.append(new_property)
#                                     st.write(f"after update row count: {len(candidates_copy)}")
                                    
#                                     if upload_to_s3(s3_client, bucket_name, candidate_file, candidates_copy):
#                                         st.cache_data.clear()
#                                         st.success(f"✅ Candidate property added successfully!")
#                                         st.rerun()
#                                 else:
#                                     comps_copy = comps.copy()
#                                     st.write(f"before update comp count: {len(comps_copy)}")
#                                     comps_copy.append(new_property)
#                                     st.write(f"after update comp count: {len(comps_copy)}")
                                    
#                                     if upload_to_s3(s3_client, bucket_name, comp_file, comps_copy):
#                                         st.cache_data.clear()
#                                         st.success(f"✅ Comp property added successfully!")
#                                         st.rerun()
                                
#                                 # Show payload preview
#                                 st.subheader("📦 Property Data Added:")
#                                 st.json(new_property)
#                             else:
#                                 st.error("❌ Failed to get coordinates for the address. Please check the address and try again.")
        
#         # === TAB 3: Candidates ===
#         with tab3:
#             st.header(f"🏠 Candidate Properties ({len(candidates)})")
#             display_properties_table(candidates, "candidate")
        
#         # === TAB 4: Comps ===
#         with tab4:
#             st.header(f"📊 Comp Properties ({len(comps)})")
#             display_properties_table(comps, "comp")
        
#         # === TAB 5: Distance Analysis ===
#         with tab5:
#             st.header("📏 Distance Analysis & Ideal Comps")
            
#             if candidates and comps:
#                 # Advanced Filter Controls
#                 st.subheader("🎛️ Advanced Filter Controls")
                
#                 # Create filter columns
#                 filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
                
#                 with filter_col1:
#                     st.write("**Distance Filter**")
#                     # Use session state for persistent filter state
#                     st.session_state.enable_distance_filter = st.checkbox(
#                         "Enable Distance Filter", 
#                         value=st.session_state.enable_distance_filter
#                     )
#                     if st.session_state.enable_distance_filter:
#                         st.session_state.max_distance = st.slider(
#                             "Max Distance (mi)", 
#                             0.5, 50.0, 
#                             value=st.session_state.max_distance, 
#                             step=0.5
#                         )
#                     else:
#                         st.session_state.max_distance = None
                
#                 with filter_col2:
#                     st.write("**Price Filter (Comps)**")
#                     st.session_state.enable_price_filter = st.checkbox(
#                         "Enable Price Filter", 
#                         value=st.session_state.enable_price_filter
#                     )
#                     if st.session_state.enable_price_filter:
#                         st.session_state.price_range = st.slider(
#                             "Comp Price Range ($)", 
#                             0, 2000000, 
#                             value=st.session_state.price_range, 
#                             step=10000, 
#                             format="$%d"
#                         )
#                         price_min, price_max = st.session_state.price_range
#                     else:
#                         price_min = price_max = None
                
#                 with filter_col3:
#                     st.write("**Size Filter (Comps)**")
#                     st.session_state.enable_size_filter = st.checkbox(
#                         "Enable Size Filter", 
#                         value=st.session_state.enable_size_filter
#                     )
#                     if st.session_state.enable_size_filter:
#                         st.session_state.size_range = st.slider(
#                             "Comp Size Range (sqft)", 
#                             200, 10000, 
#                             value=st.session_state.size_range, 
#                             step=50
#                         )
#                         size_min, size_max = st.session_state.size_range
#                     else:
#                         size_min = size_max = None
                
#                 with filter_col4:
#                     st.write("**Year Filter (Comps)**")
#                     st.session_state.enable_year_filter = st.checkbox(
#                         "Enable Year Filter", 
#                         value=st.session_state.enable_year_filter
#                     )
#                     if st.session_state.enable_year_filter:
#                         st.session_state.year_range = st.slider(
#                             "Comp Year Range", 
#                             1900, 2030, 
#                             value=st.session_state.year_range, 
#                             step=1
#                         )
#                         year_min, year_max = st.session_state.year_range
#                     else:
#                         year_min = year_max = None
                
#                 # Apply filters to candidates (no filters, just show all)
#                 filtered_candidates = candidates
                
#                 st.divider()
                
#                 # Display filter results summary
#                 col_summary1, col_summary2 = st.columns(2)
#                 with col_summary1:
#                     st.metric("Total Candidates", len(candidates))
#                 with col_summary2:
#                     st.metric("Total Comps", len(comps))
                
#                 # Two-column layout
#                 col1, col2 = st.columns([1, 1])
                
#                 with col1:
#                     st.subheader(f"🏠 Select Candidate Property ({len(filtered_candidates)} total)")
                    
#                     # Search box for candidates
#                     search_term = st.text_input("🔍 Search candidates by address", placeholder="Type to search...")
                    
#                     # Filter candidates by search term
#                     display_candidates = filtered_candidates
#                     if search_term:
#                         display_candidates = [c for c in filtered_candidates 
#                                             if search_term.lower() in c['Address'].lower()]
                    
#                     # Pagination for large datasets
#                     candidates_per_page = 10
#                     total_pages = math.ceil(len(display_candidates) / candidates_per_page)
                    
#                     if total_pages > 1:
#                         page = st.selectbox(f"Page (showing {len(display_candidates)} candidates)", 
#                                         range(1, total_pages + 1), index=0)
#                         start_idx = (page - 1) * candidates_per_page
#                         end_idx = start_idx + candidates_per_page
#                         page_candidates = display_candidates[start_idx:end_idx]
#                     else:
#                         page_candidates = display_candidates
                    
#                     # Display candidates with selection
#                     if page_candidates:
#                         for i, candidate in enumerate(page_candidates):
#                             # Find the original index in the full candidates list
#                             original_idx = next((idx for idx, c in enumerate(candidates) 
#                                             if c['Address'] == candidate['Address']), None)
#                             is_selected = st.session_state.selected_candidate_idx == original_idx
                            
#                             with st.container():
#                                 # Create two columns: property info and action buttons
#                                 prop_col, btn_col = st.columns([3, 1])
                                
#                                 with prop_col:
#                                     # Display candidate info
#                                     st.markdown(f"""
#                                     <div style="border: {'2px solid #646cff' if is_selected else '1px solid #ddd'}; 
#                                             border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;
#                                             background-color: {'#f0f8ff' if is_selected else '#f9f9f9'};">
#                                         <div style="font-weight: bold; font-size: 0.9rem; margin-bottom: 0.25rem;">
#                                             {candidate['Address']}
#                                         </div>
#                                         <div style="font-size: 0.8rem; color: #666;">
#                                             {candidate['Size (sqft)']:,} sqft • ${candidate['Price']:,} • 
#                                             ${candidate.get('Price/SqFt', 0):.0f}/sqft
#                                             {f" • Built: {candidate['Year Built']}" if candidate.get('Year Built') else ""}
#                                             {f" • {candidate['Bedrooms']} beds" if candidate.get('Bedrooms') else ""}
#                                     </div>
#                                     """, unsafe_allow_html=True)
                                
#                                 with btn_col:
#                                     # Action buttons in vertical layout (to avoid nesting columns too deep)
#                                     if st.button("Select", key=f"select_candidate_{original_idx}", 
#                                                 type="primary" if is_selected else "secondary",
#                                                 help="Select this candidate",
#                                                 use_container_width=True):
#                                         st.session_state.selected_candidate_idx = original_idx
#                                         st.rerun()
                                    
#                                     # View button with proper link handling
#                                     if candidate.get('URL'):
#                                         st.link_button("View", candidate['URL'], 
#                                                     help="View property listing",
#                                                     use_container_width=True)
#                                     else:
#                                         st.button("View", key=f"view_candidate_{original_idx}",
#                                                 disabled=True, help="No URL available",
#                                                 use_container_width=True)
                                    
#                                     # Send to Podio button
#                                     if st.button("Podio", key=f"podio_candidate_{original_idx}",
#                                                 help="Send to Podio",
#                                                 use_container_width=True):
#                                         success, message = send_to_podio(candidate)
#                                         if success:
#                                             st.success(message)
#                                         else:
#                                             st.error(message)
#                     else:
#                         st.info("No candidates match your search.")
                
#                 with col2:
#                     st.subheader("🎯 Ideal Comps & Distance Analysis")
                    
#                     if st.session_state.selected_candidate_idx is not None:
#                         selected_candidate = candidates[st.session_state.selected_candidate_idx]
                        
#                         # Display selected candidate info
#                         st.success(f"**Selected:** {selected_candidate['Address']}")
                        
#                         # Selected candidate metrics
#                         metric_col1, metric_col2, metric_col3 = st.columns(3)
#                         with metric_col1:
#                             st.metric("Size", f"{selected_candidate['Size (sqft)']:,} sqft")
#                         with metric_col2:
#                             st.metric("Price", f"${selected_candidate['Price']:,}")
#                         with metric_col3:
#                             if selected_candidate.get('Year Built'):
#                                 st.metric("Built", selected_candidate['Year Built'])
                        
#                         # Apply all filters to comps including distance
#                         distance_filter = st.session_state.max_distance if st.session_state.enable_distance_filter else None
#                         filtered_comps = filter_comps(
#                             comps, selected_candidate, price_min, price_max, size_min, size_max, 
#                             year_min, year_max, distance_filter
#                         )
                        
#                         # Find ideal comps from filtered comps (with updated criteria)
#                         ideal_comps = find_ideal_comps(selected_candidate, filtered_comps, None)  # Don't apply distance again
                        
#                         st.subheader(f"🎯 Ideal Comps Found: {len(ideal_comps)}")
                        
#                         # Show criteria (updated to include price criteria)
#                         candidate_size = selected_candidate.get('Size (sqft)', 0)
#                         candidate_year = selected_candidate.get('Year Built', None)
#                         candidate_price = selected_candidate.get('Price', 0)
                        
#                         criteria_parts = [
#                             f"Size {candidate_size - 250:,} - {candidate_size + 250:,} sqft",
#                             f"Price >= ${candidate_price + 50000:,}"
#                         ]
#                         if candidate_year:
#                             criteria_parts.append(f"Year {candidate_year - 15} - {candidate_year + 15}")
#                         else:
#                             criteria_parts.append("Any year")
                        
#                         # Add filter criteria
#                         filter_parts = []
#                         if st.session_state.enable_price_filter:
#                             filter_parts.append(f"Price ${price_min:,} - ${price_max:,}")
#                         if st.session_state.enable_size_filter:
#                             filter_parts.append(f"Size {size_min:,} - {size_max:,} sqft")
#                         if st.session_state.enable_year_filter:
#                             filter_parts.append(f"Year {year_min} - {year_max}")
#                         if st.session_state.enable_distance_filter:
#                             filter_parts.append(f"Max Distance {st.session_state.max_distance} mi")
                        
#                         criteria_text = "**Ideal Comp Criteria:** " + ", ".join(criteria_parts)
#                         if filter_parts:
#                             criteria_text += f"\n\n**Additional Filters:** " + ", ".join(filter_parts)
                        
#                         st.info(criteria_text)
                        
#                         if ideal_comps:
#                             # Calculate comp metrics
#                             comp_prices = [c['Price'] for c in ideal_comps]
#                             comp_sizes = [c['Size (sqft)'] for c in ideal_comps]
#                             comp_price_sqft = [c.get('Price/SqFt', 0) for c in ideal_comps]
                            
#                             # Display comp metrics
#                             comp_col1, comp_col2, comp_col3 = st.columns(3)
#                             with comp_col1:
#                                 st.metric("Avg Comp Price", f"${sum(comp_prices)/len(comp_prices):,.0f}")
#                             with comp_col2:
#                                 st.metric("Avg Comp Size", f"{sum(comp_sizes)/len(comp_sizes):,.0f} sqft")
#                             with comp_col3:
#                                 st.metric("Avg Comp $/sqft", f"${sum(comp_price_sqft)/len(comp_price_sqft):.0f}")
                            
#                             # Sort by distance if available
#                             if ideal_comps and 'Distance' in ideal_comps[0]:
#                                 ideal_comps.sort(key=lambda x: x.get('Distance', float('inf')))
                            
#                             # Display ideal comps in comprehensive table format
#                             comp_data = []
#                             for comp in ideal_comps:
#                                 distance = comp.get('Distance')
#                                 distance_display = f"{distance:.2f}" if distance is not None else 'N/A'
                                
#                                 # Calculate differences
#                                 size_diff = comp['Size (sqft)'] - selected_candidate['Size (sqft)']
#                                 price_diff = comp['Price'] - selected_candidate['Price']
#                                 price_sqft_diff = comp.get('Price/SqFt', 0) - selected_candidate.get('Price/SqFt', 0)
#                                 year_diff = ""
#                                 if comp.get('Year Built') and selected_candidate.get('Year Built'):
#                                     year_diff = comp['Year Built'] - selected_candidate['Year Built']
                                
#                                 # Add ALL available fields from comp
#                                 row_data = {
#                                     'Address': comp['Address'],
#                                     'Distance (mi)': distance_display,
#                                     'Size (sqft)': f"{comp['Size (sqft)']:,}",
#                                     'Size Δ': f"{size_diff:+,}",
#                                     'Price': f"${comp['Price']:,}",
#                                     'Price Δ': f"${price_diff:+,}",
#                                     'Price/SqFt': f"${comp.get('Price/SqFt', 0):.0f}",
#                                     '$/SqFt Δ': f"${price_sqft_diff:+.0f}",
#                                     'Year Built': comp.get('Year Built', ''),
#                                     'Year Δ': f"{year_diff:+d}" if year_diff != "" else "",
#                                     'Bedrooms': comp.get('Bedrooms', ''),
#                                     'Agent Name': comp.get('Agent Name', ''),
#                                     'Sold Date': comp.get('Sold Date', ''),
#                                     'Snapshot Date': comp.get('Snapshot Date', ''),
#                                     'URL': comp.get('URL', '')
#                                 }
#                                 comp_data.append(row_data)
                            
#                             comp_df = pd.DataFrame(comp_data)
                            
#                             st.dataframe(
#                                 comp_df,
#                                 use_container_width=True,
#                                 column_config={
#                                     "URL": st.column_config.LinkColumn(
#                                         "View",
#                                         help="Click to view property listing",
#                                         validate="^https://.*",
#                                         display_text="🔗"
#                                     ),
#                                     "Distance (mi)": st.column_config.TextColumn("Distance", width="small"),
#                                     "Size Δ": st.column_config.TextColumn("Size Δ", width="small"),
#                                     "Price Δ": st.column_config.TextColumn("Price Δ", width="small"),
#                                     "$/SqFt Δ": st.column_config.TextColumn("$/SqFt Δ", width="small"),
#                                     "Year Δ": st.column_config.TextColumn("Year Δ", width="small")
#                                 },
#                                 hide_index=True
#                             )
                            
#                         else:
#                             st.warning("No ideal comps found for this candidate with the current criteria.")
#                             st.info("Try adjusting the filter criteria to find more comps.")
#                     else:
#                         st.info("👆 Select a candidate property to see ideal comps and distance analysis.")
#             else:
#                 st.info("Add both candidate and comp properties to perform distance analysis.")

#     # Sidebar summary (only show when logged in)
#     if st.session_state.logged_in:
#         st.sidebar.markdown("---")
#         st.sidebar.info(
#             f"📊 **Data Summary**\n\n"
#             f"🏠 Candidates: {len(candidates)}\n\n"
#             f"📊 Comps: {len(comps)}\n\n"
#             f"💾 S3 Bucket: {bucket_name}"
#         )

# if __name__ == "__main__":
#     main()
import streamlit as st
import boto3
import pandas as pd
import json
import requests
import math
from datetime import date
import plotly.express as px

# === Page Configuration ===
st.set_page_config(
    page_title="Lonestar Real Estate - Property Manager",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === AWS Configuration ===
@st.cache_resource
def init_s3_client():
    return boto3.client(
        's3',
        region_name='us-east-1',
        aws_access_key_id=st.secrets.get("AWS_ACCESS_KEY_ID", "your_access_key"),
        aws_secret_access_key=st.secrets.get("AWS_SECRET_ACCESS_KEY", "your_secret_key")
    )

# === S3 Operations ===
def download_from_s3(s3_client, bucket_name, file_key):
    """Download existing JSON file from S3"""
    try:
        obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        raw_data = obj['Body'].read()
        data = json.loads(raw_data)
        return data
    except s3_client.exceptions.NoSuchKey:
        return []
    except Exception as e:
        st.error(f"Error reading {file_key}: {e}")
        return []

def upload_to_s3(s3_client, bucket_name, file_key, data):
    """Upload updated JSON back to S3"""
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=json.dumps(data, indent=2).encode('utf-8'),
            ContentType='application/json'
        )
        return True
    except Exception as e:
        st.error(f"Error uploading {file_key}: {e}")
        return False

# === LocationIQ Integration ===
def get_coordinates(address, api_key):
    """Get coordinates from LocationIQ API"""
    if not api_key:
        st.error("LocationIQ API key not configured")
        return None, None
    
    try:
        params = {
            'key': api_key,
            'q': address,
            'format': 'json',
            'limit': 1
        }
        
        response = requests.get('https://us1.locationiq.com/v1/search.php', params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return lat, lon
            else:
                st.error("No coordinates found for this address")
                return None, None
        else:
            st.error(f"LocationIQ API error: {response.status_code}")
            return None, None
            
    except Exception as e:
        st.error(f"Error fetching coordinates: {e}")
        return None, None

# === Distance Calculation ===
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance using Haversine formula"""
    R = 3959  # Earth's radius in miles
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return round(distance, 2)

# === Ideal Comp Filtering ===
def find_ideal_comps(candidate, comps, max_distance=None):
    """Find ideal comps based on size, year built, and distance criteria"""
    ideal_comps = []
    
    candidate_size = candidate.get('Size (sqft)', 0)
    candidate_year = candidate.get('Year Built', None)
    candidate_price = candidate.get('Price', 0)
    candidate_lat = candidate.get('Latitude')
    candidate_lon = candidate.get('Longitude')
    
    for comp in comps:
        comp_size = comp.get('Size (sqft)', 0)
        comp_year = comp.get('Year Built', None)
        comp_price = comp.get('Price', 0)
        comp_lat = comp.get('Latitude')
        comp_lon = comp.get('Longitude')
        
        # Size criteria: ±1000 sqft
        size_match = abs(comp_size - candidate_size) <= 250
        
        # Year built criteria: ±25 years (if both have year built)
        year_match = True  # Default to True if either doesn't have year
        if candidate_year and comp_year:
            year_match = abs(comp_year - candidate_year) <= 15

        price_match = True  # Default to True if either doesn't have year
        if candidate_price and comp_price:
            price_match = (comp_price - candidate_price) >= 50000     
        
        # Distance criteria (if specified)
        distance_match = True
        distance = None
        if max_distance and candidate_lat and candidate_lon and comp_lat and comp_lon:
            distance = calculate_distance(candidate_lat, candidate_lon, comp_lat, comp_lon)
            distance_match = distance <= max_distance
        
        if size_match and year_match and distance_match and price_match:
            comp_with_distance = comp.copy()
            if distance is not None:
                comp_with_distance['Distance'] = distance
            elif candidate_lat and candidate_lon and comp_lat and comp_lon:
                comp_with_distance['Distance'] = calculate_distance(candidate_lat, candidate_lon, comp_lat, comp_lon)
            ideal_comps.append(comp_with_distance)
    
    return ideal_comps


# === Property Table Display ===
def display_properties_table(properties, property_type):
    """Display properties in a compact table format with metrics"""
    if not properties:
        st.info(f"No {property_type} properties found.")
        return
    
    # Calculate and display metrics
    df_raw = pd.DataFrame(properties)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_price = df_raw['Price'].mean()
        st.metric("Avg Price", f"${avg_price:,.0f}")
    with col2:
        avg_size = df_raw['Size (sqft)'].mean()
        st.metric("Avg Size", f"{avg_size:,.0f} sqft")
    with col3:
        avg_price_sqft = df_raw['Price/SqFt'].mean()
        st.metric("Avg Price/SqFt", f"${avg_price_sqft:.0f}")
    with col4:
        total_count = len(df_raw)
        st.metric("Total Properties", total_count)
    
    # Convert to display format - showing ALL columns
    df_data = []
    for prop in properties:
        row = {}
        # Add all available fields
        for key, value in prop.items():
            if key == 'Price':
                row[key] = f"${value:,}"
            elif key == 'Size (sqft)':
                row[key] = f"{value:,}"
            elif key == 'Price/SqFt':
                row[key] = f"${value:.0f}"
            elif isinstance(value, (int, float)) and key not in ['Latitude', 'Longitude']:
                row[key] = f"{value:,}" if value > 1000 else str(value)
            else:
                row[key] = str(value) if value is not None else ''
        df_data.append(row)
    
    df = pd.DataFrame(df_data)
    
    # Display with clickable links
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "URL": st.column_config.LinkColumn(
                "View Listing",
                help="Click to view property listing",
                validate="^https://.*",
                max_chars=100,
                display_text="🔗 View"
            ),
            "Address": st.column_config.TextColumn(
                "Address",
                width="large"
            ),
            "Size (sqft)": st.column_config.TextColumn(
                "Size (sqft)",
                width="small"
            ),
            "Price": st.column_config.TextColumn(
                "Price",
                width="medium"
            ),
            "Price/SqFt": st.column_config.TextColumn(
                "Price/SqFt",
                width="small"
            )
        },
        hide_index=True
    )



# === Filter Functions ===
def filter_comps(comps, candidate, price_min=None, price_max=None, size_min=None, size_max=None, 
                 year_min=None, year_max=None, max_distance=None):
    """Filter comps based on criteria and calculate distances"""
    filtered = []
    
    candidate_lat = candidate.get('Latitude')
    candidate_lon = candidate.get('Longitude')
    
    for comp in comps:
        # Apply price filter
        if price_min is not None and comp.get('Price', 0) < price_min:
            continue
        if price_max is not None and comp.get('Price', 0) > price_max:
            continue
            
        # Apply size filter
        if size_min is not None and comp.get('Size (sqft)', 0) < size_min:
            continue
        if size_max is not None and comp.get('Size (sqft)', 0) > size_max:
            continue
            
        # Apply year filter
        if year_min is not None and (not comp.get('Year Built') or comp.get('Year Built') < year_min):
            continue
        if year_max is not None and (not comp.get('Year Built') or comp.get('Year Built') > year_max):
            continue
        
        # Calculate distance and apply distance filter
        comp_lat = comp.get('Latitude')
        comp_lon = comp.get('Longitude')
        
        if candidate_lat and candidate_lon and comp_lat and comp_lon:
            distance = calculate_distance(candidate_lat, candidate_lon, comp_lat, comp_lon)
            if max_distance is not None and distance > max_distance:
                continue
            
            # Add distance to comp data
            comp_with_distance = comp.copy()
            comp_with_distance['Distance'] = distance
            filtered.append(comp_with_distance)
        else:
            # If no coordinates, include if no distance filter
            if max_distance is None:
                filtered.append(comp)
    
    return filtered

APP_ID = st.secrets.get("PODIO_APP_ID")
APP_TOKEN = st.secrets.get("PODIO_APP_TOKEN")
CLIENT_ID = st.secrets.get("PODIO_CLIENT_ID")
CLIENT_SECRET = st.secrets.get("PODIO_CLIENT_SECRET")

# Step 1: Authenticate and get access token
def get_access_token():
    try:
        import requests
        response = requests.post(
            "https://podio.com/oauth/token",
            data={
                "grant_type": "app",
                "app_id": APP_ID,
                "app_token": APP_TOKEN,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET
            }
        )
        return response.json()["access_token"]
    except Exception as e:
        st.error(f"Error getting access token: {str(e)}")
        return None

# Helper function to convert date to Podio datetime format
def convertToPodioDatetime(date_string):
    """Convert date string to Podio datetime format"""
    try:
        from datetime import datetime
        if date_string:
            # Adjust this based on your date format
            dt = datetime.strptime(str(date_string), "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return None
    except:
        return None

# Step 2: Post item to Podio app
def send_to_podio(data):
    try:
        import requests
        access_token = get_access_token()
        if not access_token:
            return False, "Failed to get access token"
            
        url = f"https://api.podio.com/item/app/{APP_ID}/"
        headers = {
            "Authorization": f"OAuth2 {access_token}",
            "Content-Type": "application/json"
        }
        
        # Build payload with only non-empty fields
        fields = {}
        
        # Address - required field, must have value
        if data.get('Address'):
            fields["address"] = data.get('Address', '')
        
        # Price - only add if has valid value
        if data.get('Price') and data.get('Price') > 0:
            fields["listing-price"] = {
                "value": data.get('Price', 0),
                "currency": "USD"
            }
        
        # Listing date - only add if has valid date
        listing_date = data.get("Listing Date") or data.get("Sold Date") or data.get("Snapshot Date")
        if listing_date and str(listing_date).strip():
            formatted_date = convertToPodioDatetime(listing_date)
            if formatted_date:
                fields["listing-date"] = {
                    "start": formatted_date,
                    "end": formatted_date
                }
        
        # Agent name - only add if has value
        if data.get("Agent Name") and str(data.get("Agent Name")).strip():
            fields["agent-name"] = data.get("Agent Name", "")
        
        # Square feet - only add if has valid value
        if data.get("Size (sqft)") and data.get("Size (sqft)") > 0:
            fields["square-feet"] = str(data.get("Size (sqft)", ""))
        
        # Format final payload
        payload = {"fields": fields}
        
        # Debug: print payload to see what's being sent
        # st.write("Debug - Payload being sent to Podio:", payload)
        
        res = requests.post(url, json=payload, headers=headers)
        
        if res.status_code == 200:
            return True, "Successfully sent to Podio!"
        else:
            return False, f"Failed to send to Podio: {res.status_code} - {res.text}"
            
    except ImportError:
        return False, "Please install 'requests' library: pip install requests"
    except Exception as e:
        return False, f"Error sending to Podio: {str(e)}"


# === Main App ===
def main():
    st.title("🏠 Lonestar Real Estate - Property Manager")
    st.markdown("Add candidate and comp properties with automatic coordinate enrichment and distance analysis.")
    
    # Configuration - Updated for folder structure
    bucket_name =  'shinka-realestate-gold' #'lonestar-realestate-test' # 
    candidate_file = 'candidate/candidate.json'
    comp_file = 'comps/comps.json'
    
    # Initialize S3 client
    s3_client = init_s3_client()
    
    # Sidebar Configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Get API key from secrets (don't show input to user)
    locationiq_api_key = st.secrets.get("LOCATIONIQ_API_KEY", "")
    
    # Load existing data
    if st.sidebar.button("🔄 Refresh Data from S3"):
        st.cache_data.clear()
    
    @st.cache_data(ttl=60)
    def load_data():
        candidates = download_from_s3(s3_client, bucket_name, candidate_file)
        comps = download_from_s3(s3_client, bucket_name, comp_file)
        return candidates, comps
    
    candidates, comps = load_data()
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔐 Login", "📝 Add Property", "🏠 Candidates", "📊 Comps", "📏 Distance Analysis"])
    
    # === TAB 1: Login ===
    with tab1:
        st.header("🔐 User Login")
        
        # Check if already logged in and show logout option
        if st.session_state.get('logged_in', False):
            col1, col2 = st.columns([1, 1])
            with col1:
                st.success(f"✅ Currently logged in as: **{st.session_state.get('username', 'Unknown')}**")
            with col2:
                if st.button("Logout", type="secondary"):
                    st.session_state.logged_in = False
                    st.session_state.username = None
                    st.rerun()
        else:
            # Show login form only if not logged in
            with st.form("login_form"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown("### Login Credentials")
                    username = st.text_input("Username", placeholder="Enter your username")
                    password = st.text_input("Password", type="password", placeholder="Enter your password")
                    
                    login_submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
                    
                    if login_submitted:
                        if username and password:
                            # Add your authentication logic here
                            if username == st.secrets.get("username") and password == st.secrets.get("password"):  # Example credentials
                                st.success("✅ Login successful!")
                                st.session_state.logged_in = True
                                st.session_state.username = username
                                st.rerun()
                            else:
                                st.error("❌ Invalid username or password")
                        else:
                            st.error("Please enter both username and password")
                
                with col2:
                    st.markdown("### System Information")
                    st.info(
                        "**Welcome to Lonestar Real Estate Property Manager**\n\n"
                        "This system allows you to:\n"
                        "- Add and manage candidate properties\n"
                        "- Track comparable properties (comps)\n"
                        "- Perform distance analysis\n"
                        "- Send data to Podio CRM\n\n"
                        "Please log in to access the system."
                    )
    
    # Check if user is logged in before showing other tabs
    if not st.session_state.get('logged_in', False):
        # Show message in other tabs if not logged in
        with tab2:
            st.warning("🔒 Please log in first to access this feature.")
            st.info("Go to the Login tab to enter your credentials.")
        
        with tab3:
            st.warning("🔒 Please log in first to access this feature.")
            st.info("Go to the Login tab to enter your credentials.")
        
        with tab4:
            st.warning("🔒 Please log in first to access this feature.")
            st.info("Go to the Login tab to enter your credentials.")
        
        with tab5:
            st.warning("🔒 Please log in first to access this feature.")
            st.info("Go to the Login tab to enter your credentials.")
        
        return  # Exit early if not logged in
    
    # === TAB 2: Add Property ===
    with tab2:
        st.header("Add New Property")
        
        # Property type selection outside the form
        property_type = st.selectbox(
            "Property Type",
            options=["candidate", "comp"],
            format_func=lambda x: "Candidate" if x == "candidate" else "Comp",
            key="property_type_selector"
        )
        
        with st.form("property_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                address = st.text_input(
                    "Address *",
                    placeholder="e.g., 123 Main St, Houston, TX 77001",
                    help="Enter the full property address (Required)"
                )
                
                size_sqft = st.number_input(
                    "Size (sq ft) *",
                    min_value=1,
                    value=None,
                    placeholder="e.g., 2500"
                )
                
                price = st.number_input(
                    "Price ($) *",
                    min_value=0,
                    value=None,
                    step=1000,
                    placeholder="e.g., 350000"
                )
                
                # Conditional date input based on property type
                if property_type == "candidate":
                    listing_date = st.date_input(
                        "Listing Date *",
                        value=date.today(),
                        help="Date when the property was listed"
                    )
                else:
                    sold_date = st.date_input(
                        "Sold Date *",
                        value=date.today(),
                        help="Date when the property was sold"
                    )
            
            with col2:
                bedrooms = st.number_input(
                    "Bedrooms (optional)",
                    min_value=0,
                    max_value=20,
                    value=None
                )
                
                year_built = st.number_input(
                    "Year Built (optional)",
                    min_value=1800,
                    max_value=2030,
                    value=None
                )
                story = st.number_input(
                    "Story (optional)",
                    min_value=1,
                    max_value=10,
                    value=None,
                    help="Number of stories/floors in the property"
                )                
                agent_name = st.text_input(
                    "Agent Name (optional)",
                    placeholder="e.g., John Smith"
                )
                

                
                # Auto-calculate price per sq ft
                if size_sqft and price:
                    price_per_sqft = round(price / size_sqft, 2)
                    st.metric("Price/SqFt (calculated)", f"${price_per_sqft}")
            
            # Submit button with dynamic text
            button_text = f"Add {property_type.title()}"
            submitted = st.form_submit_button(
                button_text, 
                type="primary",
                use_container_width=True
            )
            
            if submitted:
                # Check for mandatory fields
                missing_fields = []
                if not address or address.strip() == "":
                    missing_fields.append("Address")
                if not size_sqft:
                    missing_fields.append("Size (sq ft)")
                if not price:
                    missing_fields.append("Price")
                
                if missing_fields:
                    st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")
                else:
                    with st.spinner(f"Adding {property_type}..."):
                        # Get coordinates
                        lat, lon = get_coordinates(address.strip(), locationiq_api_key)
                        
                        if lat is not None and lon is not None:
                            # Create property payload
                            new_property = {
                                "Address": address.strip(),
                                "Size (sqft)": size_sqft,
                                "Price": price,
                                "Price/SqFt": round(price / size_sqft, 2),
                                "Latitude": lat,
                                "Longitude": lon,
                                "Snapshot Date": str(date.today())
                            }
                            
                            # Add optional fields
                            if bedrooms:
                                new_property["Bedrooms"] = bedrooms
                            if year_built:
                                new_property["Year Built"] = year_built
                            if agent_name and agent_name.strip():
                                new_property["Agent Name"] = agent_name.strip()
                            if story:
                                new_property["Story"] = story
                            
                            # Add type-specific fields with user-provided dates
                            if property_type == "candidate":
                                new_property["Listing Date"] = str(listing_date)
                                new_property["URL"] = f"https://www.har.com/mapsearch?quicksearch={address.replace(' ', '+')}&view=map"
                            else:
                                new_property["Sold Date"] = str(sold_date)
                                new_property["URL"] = f"https://www.har.com/mapsearch?quicksearch={address.replace(' ', '+')}&view=map"
                            
                            # Add to existing data
                            if property_type == "candidate":
                                candidates_copy = candidates.copy()
                                st.write(f"before update row count: {len(candidates_copy)}")
                                candidates_copy.append(new_property)
                                st.write(f"after update row count: {len(candidates_copy)}")
                                
                                if upload_to_s3(s3_client, bucket_name, candidate_file, candidates_copy):
                                    st.cache_data.clear()
                                    st.success(f"✅ Candidate property added successfully!")
                                    st.rerun()
                            else:
                                comps_copy = comps.copy()
                                st.write(f"before update comp count: {len(comps_copy)}")
                                comps_copy.append(new_property)
                                st.write(f"after update comp count: {len(comps_copy)}")
                                
                                if upload_to_s3(s3_client, bucket_name, comp_file, comps_copy):
                                    st.cache_data.clear()
                                    st.success(f"✅ Comp property added successfully!")
                                    st.rerun()
                            
                            # Show payload preview
                            st.subheader("📦 Property Data Added:")
                            st.json(new_property)
                        else:
                            st.error("❌ Failed to get coordinates for the address. Please check the address and try again.")
    
    # === TAB 3: Candidates ===
    with tab3:
        st.header(f"🏠 Candidate Properties ({len(candidates)})")
        display_properties_table(candidates, "candidate")
    
    # === TAB 4: Comps ===
    with tab4:
        st.header(f"📊 Comp Properties ({len(comps)})")
        display_properties_table(comps, "comp")
    
    # === TAB 5: Distance Analysis ===
    with tab5:
        st.header("📏 Distance Analysis & Ideal Comps")
        
        if candidates and comps:
            # Advanced Filter Controls
            st.subheader("🎛️ Advanced Filter Controls")
            
            # Create filter columns
            filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
            
            with filter_col1:
                st.write("**Distance Filter**")
                enable_distance_filter = st.checkbox("Enable Distance Filter", value=True, key="enable_distance_filter")
                max_distance = st.slider("Max Distance (mi)", 0.5, 50.0, 10.0, 0.5, disabled=not enable_distance_filter)
            
            with filter_col2:
                st.write("**Price Filter (Comps)**")
                enable_price_filter = st.checkbox("Enable Price Filter", value=False)
                if enable_price_filter:
                    price_range = st.slider("Comp Price Range ($)", 0, 2000000, (50000, 1000000), 10000, format="$%d")
                    price_min, price_max = price_range
                else:
                    price_min = price_max = None
            
            with filter_col3:
                st.write("**Size Filter (Comps)**")
                enable_size_filter = st.checkbox("Enable Size Filter", value=False)
                if enable_size_filter:
                    size_range = st.slider("Comp Size Range (sqft)", 200, 10000, (800, 4000), 50)
                    size_min, size_max = size_range
                else:
                    size_min = size_max = None
            
            with filter_col4:
                st.write("**Year Filter (Comps)**")
                enable_year_filter = st.checkbox("Enable Year Filter", value=False)
                if enable_year_filter:
                    year_range = st.slider("Comp Year Range", 1900, 2030, (1980, 2020), 1)
                    year_min, year_max = year_range
                else:
                    year_min = year_max = None
            
            # Apply filters to candidates (no filters, just show all)
            filtered_candidates = candidates
            
            st.divider()
            
            # Display filter results summary
            col_summary1, col_summary2 = st.columns(2)
            with col_summary1:
                st.metric("Total Candidates", len(candidates))
            with col_summary2:
                st.metric("Total Comps", len(comps))
            
            # Two-column layout
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader(f"🏠 Select Candidate Property ({len(filtered_candidates)} total)")
                
                # Initialize session state
                if 'selected_candidate_idx' not in st.session_state:
                    st.session_state.selected_candidate_idx = None
                
                # Search box for candidates
                search_term = st.text_input("🔍 Search candidates by address", placeholder="Type to search...")
                
                # Filter candidates by search term
                display_candidates = filtered_candidates
                if search_term:
                    display_candidates = [c for c in filtered_candidates 
                                        if search_term.lower() in c['Address'].lower()]
                
                # Pagination for large datasets
                candidates_per_page = 10
                total_pages = math.ceil(len(display_candidates) / candidates_per_page)
                
                if total_pages > 1:
                    page = st.selectbox(f"Page (showing {len(display_candidates)} candidates)", 
                                    range(1, total_pages + 1), index=0)
                    start_idx = (page - 1) * candidates_per_page
                    end_idx = start_idx + candidates_per_page
                    page_candidates = display_candidates[start_idx:end_idx]
                else:
                    page_candidates = display_candidates
                
                # Display candidates with selection
                if page_candidates:
                    for i, candidate in enumerate(page_candidates):
                        # Find the original index in the full candidates list
                        original_idx = next((idx for idx, c in enumerate(candidates) 
                                        if c['Address'] == candidate['Address']), None)
                        is_selected = st.session_state.selected_candidate_idx == original_idx
                        
                        with st.container():
                            # Create two columns: property info and action buttons
                            prop_col, btn_col = st.columns([3, 1])
                            
                            with prop_col:
                                # Display candidate info
                                st.markdown(f"""
                                <div style="border: {'2px solid #646cff' if is_selected else '1px solid #ddd'}; 
                                        border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;
                                        background-color: {'#f0f8ff' if is_selected else '#f9f9f9'};">
                                    <div style="font-weight: bold; font-size: 0.9rem; margin-bottom: 0.25rem;">
                                        {candidate['Address']}
                                    </div>
                                    <div style="font-size: 0.8rem; color: #666;">
                                        {candidate['Size (sqft)']:,} sqft • ${candidate['Price']:,} • 
                                        ${candidate.get('Price/SqFt', 0):.0f}/sqft
                                        {f" • Built: {candidate['Year Built']}" if candidate.get('Year Built') else ""}
                                        {f" • {candidate['Bedrooms']} beds" if candidate.get('Bedrooms') else ""}
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with btn_col:
                                # Action buttons in vertical layout (to avoid nesting columns too deep)
                                if st.button("Select", key=f"select_candidate_{original_idx}", 
                                            type="primary" if is_selected else "secondary",
                                            help="Select this candidate",
                                            use_container_width=True):
                                    st.session_state.selected_candidate_idx = original_idx
                                    st.rerun()
                                
                                # View button with proper link handling
                                if candidate.get('URL'):
                                    st.link_button("View", candidate['URL'], 
                                                help="View property listing",
                                                use_container_width=True)
                                else:
                                    st.button("View", key=f"view_candidate_{original_idx}",
                                            disabled=True, help="No URL available",
                                            use_container_width=True)
                                
                                # Send to Podio button
                                if st.button("Podio", key=f"podio_candidate_{original_idx}",
                                            help="Send to Podio",
                                            use_container_width=True):
                                    success, message = send_to_podio(candidate)
                                    if success:
                                        st.success(message)
                                    else:
                                        st.error(message)
                else:
                    st.info("No candidates match your search.")
            
            with col2:
                st.subheader("🎯 Ideal Comps & Distance Analysis")
                
                if st.session_state.selected_candidate_idx is not None:
                    selected_candidate = candidates[st.session_state.selected_candidate_idx]
                    
                    # Display selected candidate info
                    st.success(f"**Selected:** {selected_candidate['Address']}")
                    
                    # Selected candidate metrics
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    with metric_col1:
                        st.metric("Size", f"{selected_candidate['Size (sqft)']:,} sqft")
                    with metric_col2:
                        st.metric("Price", f"${selected_candidate['Price']:,}")
                    with metric_col3:
                        if selected_candidate.get('Year Built'):
                            st.metric("Built", selected_candidate['Year Built'])
                    
                    # Apply all filters to comps including distance
                    distance_filter = max_distance if enable_distance_filter else None
                    filtered_comps = filter_comps(
                        comps, selected_candidate, price_min, price_max, size_min, size_max, 
                        year_min, year_max, distance_filter
                    )
                    
                    # Find ideal comps from filtered comps (with updated criteria)
                    ideal_comps = find_ideal_comps(selected_candidate, filtered_comps, None)  # Don't apply distance again
                    
                    st.subheader(f"🎯 Ideal Comps Found: {len(ideal_comps)}")
                    
                    # Show criteria (updated to include price criteria)
                    candidate_size = selected_candidate.get('Size (sqft)', 0)
                    candidate_year = selected_candidate.get('Year Built', None)
                    candidate_price = selected_candidate.get('Price', 0)
                    
                    criteria_parts = [
                        f"Size {candidate_size - 250:,} - {candidate_size + 250:,} sqft",
                        f"Price >= ${candidate_price + 50000:,}"
                    ]
                    if candidate_year:
                        criteria_parts.append(f"Year {candidate_year - 15} - {candidate_year + 15}")
                    else:
                        criteria_parts.append("Any year")
                    
                    # Add filter criteria
                    filter_parts = []
                    if enable_price_filter:
                        filter_parts.append(f"Price ${price_min:,} - ${price_max:,}")
                    if enable_size_filter:
                        filter_parts.append(f"Size {size_min:,} - {size_max:,} sqft")
                    if enable_year_filter:
                        filter_parts.append(f"Year {year_min} - {year_max}")
                    if enable_distance_filter:
                        filter_parts.append(f"Max Distance {max_distance} mi")
                    
                    criteria_text = "**Ideal Comp Criteria:** " + ", ".join(criteria_parts)
                    if filter_parts:
                        criteria_text += f"\n\n**Additional Filters:** " + ", ".join(filter_parts)
                    
                    st.info(criteria_text)
                    
                    if ideal_comps:
                        # Calculate comp metrics
                        comp_prices = [c['Price'] for c in ideal_comps]
                        comp_sizes = [c['Size (sqft)'] for c in ideal_comps]
                        comp_price_sqft = [c.get('Price/SqFt', 0) for c in ideal_comps]
                        
                        # Display comp metrics
                        comp_col1, comp_col2, comp_col3 = st.columns(3)
                        with comp_col1:
                            st.metric("Avg Comp Price", f"${sum(comp_prices)/len(comp_prices):,.0f}")
                        with comp_col2:
                            st.metric("Avg Comp Size", f"{sum(comp_sizes)/len(comp_sizes):,.0f} sqft")
                        with comp_col3:
                            st.metric("Avg Comp $/sqft", f"${sum(comp_price_sqft)/len(comp_price_sqft):.0f}")
                        
                        # Sort by distance if available
                        if ideal_comps and 'Distance' in ideal_comps[0]:
                            ideal_comps.sort(key=lambda x: x.get('Distance', float('inf')))
                        
                        # Display ideal comps in comprehensive table format
                        comp_data = []
                        for comp in ideal_comps:
                            distance = comp.get('Distance')
                            distance_display = f"{distance:.2f}" if distance is not None else 'N/A'
                            
                            # Calculate differences
                            size_diff = comp['Size (sqft)'] - selected_candidate['Size (sqft)']
                            price_diff = comp['Price'] - selected_candidate['Price']
                            price_sqft_diff = comp.get('Price/SqFt', 0) - selected_candidate.get('Price/SqFt', 0)
                            year_diff = ""
                            if comp.get('Year Built') and selected_candidate.get('Year Built'):
                                year_diff = comp['Year Built'] - selected_candidate['Year Built']
                            
                            # Add ALL available fields from comp
                            row_data = {
                                'Address': comp['Address'],
                                'Distance (mi)': distance_display,
                                'Size (sqft)': f"{comp['Size (sqft)']:,}",
                                'Size Δ': f"{size_diff:+,}",
                                'Price': f"${comp['Price']:,}",
                                'Price Δ': f"${price_diff:+,}",
                                'Price/SqFt': f"${comp.get('Price/SqFt', 0):.0f}",
                                '$/SqFt Δ': f"${price_sqft_diff:+.0f}",
                                'Year Built': comp.get('Year Built', ''),
                                'Year Δ': f"{year_diff:+d}" if year_diff != "" else "",
                                'Bedrooms': comp.get('Bedrooms', ''),
                                'Agent Name': comp.get('Agent Name', ''),
                                'Sold Date': comp.get('Sold Date', ''),
                                'Snapshot Date': comp.get('Snapshot Date', ''),
                                'URL': comp.get('URL', '')
                            }
                            comp_data.append(row_data)
                        
                        comp_df = pd.DataFrame(comp_data)
                        
                        st.dataframe(
                            comp_df,
                            use_container_width=True,
                            column_config={
                                "URL": st.column_config.LinkColumn(
                                    "View",
                                    help="Click to view property listing",
                                    validate="^https://.*",
                                    display_text="🔗"
                                ),
                                "Distance (mi)": st.column_config.TextColumn("Distance", width="small"),
                                "Size Δ": st.column_config.TextColumn("Size Δ", width="small"),
                                "Price Δ": st.column_config.TextColumn("Price Δ", width="small"),
                                "$/SqFt Δ": st.column_config.TextColumn("$/SqFt Δ", width="small"),
                                "Year Δ": st.column_config.TextColumn("Year Δ", width="small")
                            },
                            hide_index=True
                        )
                        
                    else:
                        st.warning("No ideal comps found for this candidate with the current criteria.")
                        st.info("Try adjusting the filter criteria to find more comps.")
                else:
                    st.info("👆 Select a candidate property to see ideal comps and distance analysis.")
        else:
            st.info("Add both candidate and comp properties to perform distance analysis.")

    st.sidebar.markdown("---")
    st.sidebar.info(
        f"📊 **Data Summary**\n\n"
        f"🏠 Candidates: {len(candidates)}\n\n"
        f"📊 Comps: {len(comps)}\n\n"
        f"💾 S3 Bucket: {bucket_name}"
    )

if __name__ == "__main__":
    main()
