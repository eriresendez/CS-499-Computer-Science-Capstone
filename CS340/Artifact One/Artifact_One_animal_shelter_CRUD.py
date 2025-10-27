from pymongo import MongoClient 
from bson.objectid import ObjectId
from io import  StringIO, BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime
import os
import pandas as pd
import json
import csv

class AnimalShelter:
    """ Enhanced CRUD operations for Animal collection in MongoDB with exporting """

        # Original project connection variables and parameters to connect with a remote MongoDB database hosted on Apporot virtual services
        
    # Utilizing local CSV files instead of MongoDB for broader compatibility and to eliminate the use of external dependencies, 
    # making it more accessible and portable
    
    def __init__(self, csv_file_path=None): 
        self.csv_file_path= csv_file_path or 'aac_shelter_outcomes.csv'
        self.data = self._load_csv_data()
        print(f"Loaded {len(self.data)} records from {self.csv_file_path}")

    """ Loading data from local CSV file instead of remote MongoDB """ 
    
    def _load_csv_data(self):
        try: 
            if os.path.exists(self.csv_file_path):
                df = pd.read_csv(self.csv_file_path)
                # clean data, remove any empty columns
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                if '' in df.columns: 
                    df.drop(columns=[''], inplace=True)
                print(f"Success: Loaded {len(df)} records from {self.csv_file_path}")
                return df.to_dict('records')
            else: 
                print(f"CSV file{self.csv_file_path} not found.")
                print("Please check VSV file path and try again")
                return []
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return []

    # Create Method to implement the C in CRUD

    def create(self, data): 
        """ Insert new document into collection """ 
        #ensuring data is valid dictionary
        if data is not None and isinstance(data, dict):
            try:
                # replacing MongoDB insert with list append for CSV data and validation statement
                self.data.append(data)
                print("Document inserted successfully") 
                return True
            except Exception as e: 
                print(f"Error querying documents: {e}")
                return False
        else: 
            raise ValueError("Invalid data. Data parameter is empty and must be non-empty dictionary.")

    # Read method to implement the R in CRUD

    def read(self, query):
        if query is not None and isinstance(query, dict):
            # ensuring query is a valid dictionary 
            try:  
                # replaced MongoDB find with filtering for csv data
                return self._filtered_data(query)
            except Exception as e: 
                print(f"Error querying documents: {e}")
                return [] # returns an empty list on failure
        else:
            raise Exception("Invalid query. Data parameter is empty and myst be non-empty dictionary.")


    def _filtered_data(self, query):
        """ 
            Filtering method, used in the read method, to replace MongoDB query functionality 
            Implements MongoDB-like query operations for local CSV data 
        """
        filtered_data = []
        
        for item in self.data:
            match = True
            for key, value in query.items():
                if key not in item: 
                    match = False
                    break

                if isinstance(value, dict):
                    # should handle operators like $in, $gte, $lte for the MongoDB-esque syntax
                    for op, op_value in value.items(): 
                        if op == '$in':
                            if item[key] not in op_value: 
                                match = False
                                break
                        elif op == '$gte':
                            try:
                                item_val = float(item[key]) if isinstance(item[key], (int, float, str)) and str(item[key]).replace('.', '').isdigit() else 0 
                                op_val= float(op_value)
                                if item_val < op_val:
                                    match = False
                                    break
                            except (ValueError, TypeError):
                                match = False
                                break
                        elif op == '$lte': 
                            try:
                                item_val = float(item[key]) if isinstance(item[key], (int, float, str)) and str(item[key]).replace('.', '').isdigit() else 0
                                op_val = float(op_value)
                                if item_val > op_val:
                                    match = False
                                    break
                            except (ValueError, TypeError):
                                match = False
                                break
                        else:
                            # Handle other operators if needed
                            if str(item[key]) != str(op_value):
                                match = False
                                break
                else:
                    # Simple equality check
                    if str(item[key]) != str(value):
                        match = False
                        break
            if match: 
                filtered_data.append(item)
                
        return filtered_data

                    
    # UPDATE method to implement the U in CRUD
    
    def update(self, query, update_data, multiple=False):
        # updating one or more documents based on query
        if not isinstance(query, dict) or not isinstance(update_data, dict):
            raise ValueError("Invalid update. Query and update data must be non-empty dictionaries.")    
            
        try: 
            # replaced the MongoDB update with custom update logic
            updated_count = 0 
            for item in self.data: 
                if self._item_matches_query(item, query):
                    item.update(update_data)
                    updated_count += 1
                    if not multiple: 
                        break
            return updated_count 
            # returns number of documents modified in the collection
        
        except Exception as e: 
            print(f"Error updating documents: {e}")
            return 0 
            # returning 0 if no documents were modified 

    def _item_matches_query(self, item, query):
        """ 
            Checks if item matches query criteria
            Used in Update and Delete methods 
        """ 
        for key, value in query.items():
            if key not in item or item[key] != value: 
               return False
        return True
    
    # Deletion method to implement the D in CRUD
    
    def delete(self, query, multiple=False):
        # delete one or many documents based on query
        if not isinstance(query, dict):
            raise ValueError("Invalid deletion. Query must be a non-empty dictionary.")
            
        try:
            deleted_count = 0
            items_to_keep = []

            for item in self.data:
                if self._item_matches_query(item, query):
                    deleted_count += 1
                    if not multiple:
                        continue
                    else: 
                        continue
                items_to_keep.append(item)

            self.data = items_to_keep
                
            return deleted_count
            # returns the number of deleted documents from the collection
        
        except Exception as e:
            print(f"Error deleting documents: {e}")
            return 0
            #returning 0 if no documents were deleted from the collection

    """ Multi-format export and PDF reporting capabilities """

    def export_to_csv(self, query=None, filename=None):
        """ 
            Export filtered data to csv format
            Will allow rescue teams to use data in spreadsheet applications
        """ 
        data = self.read(query if query else{})
        if not data: 
            return "No data available to export"

        df = pd.DataFrame(data)

        if filename: 
            df.to_csv(filename, index=False)
            return f"Data exported to {filename}"

        else: 
            #return CSV as string for immediate download
            output = StringIO()
            df.to_csv(output, index=False)
            return output.getvalue()

    def export_to_json(self, query=None, filename=None):
        """ Export filtered data to JSON format """

        data = self.read(query if query else{})
        if not data: 
            return "No data available for export"

        if filename: 
            with open(filename, 'w') as f: 
                json.dump(data, f, indent=2)
            return f"Data exported to {filename}"

        else: 
            return json.dumps(data, indent=2)

    def export_to_excel(self, query=None, filename="animal_data.xlsx"):
        """ Exporting filtered data to excel format """
        data = self.read(query if query else{})
        if not data: 
            return "No data available for export"

        df = pd.DataFrame(data)

        df.to_excel(filename, index=False)
        return f"Data exported to {filename}"

    def generate_rescue_report_pdf(self, query=None, filename="rescue_report.pdf"):
        """ 
            Generate PDF report for recue team briefings
            Creates a printable summary with statistics and animal data for operational planning
        """ 
        data = self.read(query if query else {})
        if not data:
            return "No data available for report generation"
        
        df = pd.DataFrame(data)
        
        # Create PDF document with organized layout
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title section. Header for rescue team documentation
        title = Paragraph("Animal Rescue Team Briefing Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Report metadata. Essential information for operational context
        metadata = Paragraph(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}<br/>"
            f"Total Animals: {len(data)}<br/>"
            f"Data Source: {self.csv_file_path}<br/>"
            f"Report Type: Rescue Operations Briefing", 
            styles['Normal']
        )
        story.append(metadata)
        story.append(Spacer(1, 20))
        
        # Summary statistics. Quick overview for rescue team planning
        if len(data) > 0:
            # Calculate operational statistics
            dog_count = len([d for d in data if d.get('animal_type') == 'Dog'])
            cat_count = len([d for d in data if d.get('animal_type') == 'Cat'])
            adoption_count = len([d for d in data if d.get('outcome_type') == 'Adoption'])
            
            summary_data = [
                ["Metric", "Value"],
                ["Total Animals", str(len(data))],
                ["Dogs", str(dog_count)],
                ["Cats", str(cat_count)],
                ["Available for Rescue", str(adoption_count)]
            ]
            
            summary_table = Table(summary_data, colWidths=[200, 100])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(Paragraph("Summary Statistics", styles['Heading2']))
            story.append(Spacer(1, 12))
            story.append(summary_table)
            story.append(Spacer(1, 20))
        
        # Animal data table. Will have detailed information for rescue operations
        key_columns = ['animal_id', 'name', 'animal_type', 'breed', 'age_upon_outcome', 'sex_upon_outcome', 'outcome_type']
        available_columns = [col for col in key_columns if col in df.columns]

        # Limit table size for PDF readability
        if available_columns and len(data) <= 50:  
            #header row
            table_data = [available_columns]  

            # Limit to first 50 records for concise reporting
            for item in data[:50]:  
                row = [str(item.get(col, '')) for col in available_columns]
                table_data.append(row)
            
            animal_table = Table(table_data, repeatRows=1)
            animal_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            
            story.append(Paragraph("Animal Data (Sample)", styles['Heading2']))
            story.append(Spacer(1, 12))
            story.append(animal_table)        
        
        # Build PDF document
        doc.build(story)
        return f"PDF report generated: {filename}"

    def generate_rescue_report_pdf_from_data(self, data, filename="rescue_report.pdf"):
        """ 
        Generate PDF report for rescue team briefings FROM PROVIDED DATA
        Creates a printable summary with statistics and animal data for operational planning
    """ 
        if not data:
            return "No data available for report generation"

        df = pd.DataFrame(data)

        #create PDF document with organized layout
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        #Title section
        title = Paragraph("Animal Rescue Team Briefing Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
    
        # Report metadata
        metadata = Paragraph(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}<br/>"
            f"Total Animals: {len(data)}<br/>"
            f"Data Source: {self.csv_file_path}<br/>"
            f"Report Type: Rescue Operations Briefing", 
            styles['Normal']
        )

        story.append(metadata)
        story.append(Spacer(1, 20))

        # Calculate rescue type counts
        water_rescue_count = self._count_water_rescue_dogs(data)
        wilderness_rescue_count = self._count_wilderness_rescue_dogs(data)
        disaster_rescue_count = self._count_disaster_rescue_dogs(data)

        # Rescue Type Statistics
        rescue_data = [
            ["Rescue Type", "Count"],
            ["Water Rescue", str(water_rescue_count)],
            ["Mountain/Wilderness Rescue", str(wilderness_rescue_count)],
            ["Disaster/Individual Tracking", str(disaster_rescue_count)],
            ["Total Rescue Dogs", str(water_rescue_count + wilderness_rescue_count + disaster_rescue_count)]
        ]
    
        rescue_table = Table(rescue_data, colWidths=[250, 100])
        rescue_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(Paragraph("Rescue Type Distribution", styles['Heading2']))
        story.append(Spacer(1, 12))
        story.append(rescue_table)
        story.append(Spacer(1, 20))
    
        # Summary statistics
        if len(data) > 0:
            dog_count = len([d for d in data if d.get('animal_type') == 'Dog'])
            cat_count = len([d for d in data if d.get('animal_type') == 'Cat'])
            adoption_count = len([d for d in data if d.get('outcome_type') == 'Adoption'])
        
            summary_data = [
                ["Metric", "Value"],
                ["Total Animals", str(len(data))],
                ["Dogs", str(dog_count)],
                ["Cats", str(cat_count)],
                ["Available for Rescue", str(adoption_count)],
                ["Rescue-Eligible Dogs", str(water_rescue_count + wilderness_rescue_count + disaster_rescue_count)]
            ]
        
            summary_table = Table(summary_data, colWidths=[200, 100])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(Paragraph("Summary Statistics", styles['Heading2']))
            story.append(Spacer(1, 12))
            story.append(summary_table)
            story.append(Spacer(1, 20))
    
        # Animal data table
        key_columns = ['animal_id', 'name', 'animal_type', 'breed', 'age_upon_outcome', 'sex_upon_outcome', 'outcome_type']
        available_columns = [col for col in key_columns if col in df.columns]

        if available_columns and len(data) <= 50:  
            table_data = [available_columns]  
            for item in data[:50]:  
                row = [str(item.get(col, '')) for col in available_columns]
                table_data.append(row)
        
            animal_table = Table(table_data, repeatRows=1)
            animal_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
        
            story.append(Paragraph("Animal Data (Sample)", styles['Heading2']))
            story.append(Spacer(1, 12))
            story.append(animal_table)        
    
        # Build PDF document
        doc.build(story)
        return f"PDF report generated: {filename}"


    def _count_water_rescue_dogs(self, data):
        """Count dogs eligible for water rescue"""
        water_breeds = ["Labrador Retriever Mix", "Chesapeake Bay Retriever", "Newfoundland"]
        count = 0
        for item in data:
            if (item.get('animal_type') == 'Dog' and
                item.get('breed') in water_breeds and
                item.get('sex_upon_outcome') == 'Intact Female'):
                # Check age if available
                age = item.get('age_upon_outcome_in_weeks')
                if age is not None:
                    try:
                        age_weeks = float(age)
                        if 26.0 <= age_weeks <= 156.0:
                            count += 1
                    except (ValueError, TypeError):
                        continue
                else:
                    count += 1
        return count

    def _count_wilderness_rescue_dogs(self, data):
        """Count dogs eligible for mountain/wilderness rescue"""
        wilderness_breeds = ["German Shepherd", "Alaskan Malamute", "Old English Sheepdog", 
                       "Siberian Husky", "Rottweiler"]
        count = 0
        for item in data:
            if (item.get('animal_type') == 'Dog' and
                item.get('breed') in wilderness_breeds and
                item.get('sex_upon_outcome') == 'Intact Male'):
                # Check age if available
                age = item.get('age_upon_outcome_in_weeks')
                if age is not None:
                    try:
                        age_weeks = float(age)
                        if 26.0 <= age_weeks <= 156.0:
                            count += 1
                    except (ValueError, TypeError):
                        continue
                else:
                    count += 1
        return count

    def _count_disaster_rescue_dogs(self, data):
        """Count dogs eligible for disaster/individual tracking"""
        disaster_breeds = ["Doberman Pinscher", "German Shepherd", "Golden Retriever", 
                     "Bloodhound", "Rottweiler"]
        count = 0
        for item in data:
            if (item.get('animal_type') == 'Dog' and
                item.get('breed') in disaster_breeds and
                item.get('sex_upon_outcome') == 'Intact Male'):
                # Check age if available
                age = item.get('age_upon_outcome_in_weeks')
                if age is not None:
                    try:
                        age_weeks = float(age)
                        if 20.0 <= age_weeks <= 300.0:
                            count += 1
                    except (ValueError, TypeError):
                        continue
                else:
                    count += 1
        return count

    def get_export_stats(self, query=None):
        """
            Generate statistics for export operations
            Provides insights about the data being exported for quality control
        """
        data = self.read(query if query else {})
        if not data:
            return {
                'total_records': 0,
                'animal_types': {},
                'outcome_types': {},
                'breeds_top': {}
            }
        
        # Calculate comprehensive statistics
        animal_types = {}
        outcome_types = {}
        breeds = {}
        
        for item in data:
            # Animal type counts
            animal_type = item.get('animal_type', 'Unknown')
            animal_types[animal_type] = animal_types.get(animal_type, 0) + 1
            
            # Outcome type counts  
            outcome_type = item.get('outcome_type', 'Unknown')
            outcome_types[outcome_type] = outcome_types.get(outcome_type, 0) + 1
            
            # Breed counts
            breed = item.get('breed', 'Unknown')
            breeds[breed] = breeds.get(breed, 0) + 1
        
        # Get top 5 breeds for quick reference
        sorted_breeds = sorted(breeds.items(), key=lambda x: x[1], reverse=True)
        top_breeds = dict(sorted_breeds[:5])
        
        stats = {
            'total_records': len(data),
            'animal_types': animal_types,
            'outcome_types': outcome_types,
            'breeds_top': top_breeds
        }
        
        return stats

        
