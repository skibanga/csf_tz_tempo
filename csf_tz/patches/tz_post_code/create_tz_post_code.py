import frappe
import os

def execute():

    script_dir = os.path.dirname(os.path.abspath(__file__))
    village_file_path = os.path.join(script_dir, 'sql/village_query.sql')
    region_file_path = os.path.join(script_dir, 'sql/region_query.sql')
    district_file_path = os.path.join(script_dir, 'sql/district_query.sql')
    ward_file_path = os.path.join(script_dir, 'sql/ward_query.sql')

    with open(region_file_path, 'r') as file:
        sql_content = file.read()
        queries = sql_content.split(';')  
        
        for query in queries:
            if query.strip(): 
                try:
                    frappe.db.sql(query)
                    frappe.db.commit()
                except Exception as e:
                    print(f"warning when running region query: {e}")  
    
    with open(district_file_path, 'r') as file:
        sql_content = file.read()
        queries = sql_content.split(';')  
        
        for query in queries:
            if query.strip(): 
                try:
                    frappe.db.sql(query)
                    frappe.db.commit()
                except Exception as e:
                    print(f"warning when running district query: {e}")     

    with open(ward_file_path, 'r') as file:
        sql_content = file.read()
        queries = sql_content.split(';')  
        
        for query in queries:
            if query.strip(): 
                try:
                    frappe.db.sql(query)
                    frappe.db.commit()
                except Exception as e:
                    print(f"warning when running ward query: {e}")     

    with open(village_file_path, 'r') as file:
        sql_content = file.read()
        queries = sql_content.split(';')  
        
        for query in queries:
            if query.strip(): 
                try:
                    frappe.db.sql(query)
                    frappe.db.commit()
                except Exception as e:
                    print(f"warning when running village query: {e}")
         
 

                      
