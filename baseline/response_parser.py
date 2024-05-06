import re

class LLMResponseParser:
    def __init__(self):
        pass

    def search_for_response(self, pattern, response_text):
        try: 
            return re.search(pattern, response_text).group(1).strip()
        except:
            return ""
    
    def format_model_response(self, folder_hash, response_text, is_error):
        if is_error:
            brand = has_credentials = has_call_to_actions = list_of_credentials = list_of_call_to_action = confidence_score = supporting_evidence = "Error Occurred"
        elif "payload size exceeds the limit" in response_text:
            brand = has_credentials = has_call_to_actions = list_of_credentials = list_of_call_to_action = confidence_score = supporting_evidence = "Payload exceeds limit"
        elif len(response_text) == 0:
            brand = has_credentials = has_call_to_actions = list_of_credentials = list_of_call_to_action = confidence_score = supporting_evidence = "Indeterminate"
        else: 
            brand = self.search_for_response(r'Brand: (.+)', response_text)
            has_credentials = self.search_for_response(r'Has_Credentials: (.+)', response_text)
            has_call_to_actions = self.search_for_response(r'Has_Call_To_Action: (.+)', response_text)
            list_of_credentials = self.search_for_response(r'List_of_credentials: (.+)', response_text)
            list_of_call_to_action = self.search_for_response(r'List_of_call_to_action: (.+)', response_text)
            confidence_score = self.search_for_response(r'Confidence_Score: (.+)', response_text)
            supporting_evidence = self.search_for_response(r'Supporting_Evidence: (.+)', response_text)
            
        return {
            "Folder Hash": folder_hash,
            "Brand": brand,
            "Has_Credentials": has_credentials,
            "Has_Call_To_Actions": has_call_to_actions,
            "List of Credentials fields": list_of_credentials,
            "List of Call-To-Actions": list_of_call_to_action,
            "Confidence Score": confidence_score,
            "Supporting Evidence": supporting_evidence
        }