#!/usr/bin/env python3
"""
SAP RFC Function Caller - Execute any RFC-enabled function module
Built by SAPCONET for enterprise SAP automation
"""

import pyrfc
import json
import sys
from typing import Dict, Any, Optional
from datetime import datetime
import pprint

class SAPRFCCaller:
    """Generic SAP RFC function module caller with result formatting"""
    
    def __init__(self, connection_params: Dict[str, str]):
        """Initialize SAP connection"""
        try:
            self.conn = pyrfc.Connection(**connection_params)
            print(f"✅ Connected to SAP system: {connection_params.get('ashost', 'Unknown')}")
        except Exception as e:
            print(f"❌ SAP connection failed: {str(e)}")
            sys.exit(1)
    
    def get_function_interface(self, function_name: str) -> Dict[str, Any]:
        """Get function module interface definition"""
        try:
            # Get function metadata
            interface = self.conn.get_function_description(function_name)
            
            result = {
                'name': function_name,
                'description': interface.get('description', ''),
                'parameters': {
                    'importing': [],
                    'exporting': [],  
                    'changing': [],
                    'tables': []
                }
            }
            
            # Parse parameters
            for param in interface.get('parameters', []):
                param_info = {
                    'name': param.get('name'),
                    'type': param.get('type_kind'),
                    'direction': param.get('direction'),
                    'optional': param.get('optional', False),
                    'description': param.get('parameter_text', ''),
                    'default': param.get('default_value', '')
                }
                
                direction = param.get('direction', '').lower()
                if direction == 'importing':
                    result['parameters']['importing'].append(param_info)
                elif direction == 'exporting':
                    result['parameters']['exporting'].append(param_info)
                elif direction == 'changing':
                    result['parameters']['changing'].append(param_info)
                elif direction == 'tables':
                    result['parameters']['tables'].append(param_info)
            
            return result
            
        except Exception as e:
            print(f"❌ Error getting function interface: {str(e)}")
            return {}
    
    def call_function(self, function_name: str, parameters: Dict[str, Any] = None,
                     save_result: bool = False, output_file: str = None) -> Dict[str, Any]:
        """
        Execute SAP function module with parameters
        
        Args:
            function_name: Name of RFC function module
            parameters: Dictionary of input parameters
            save_result: Whether to save result to file
            output_file: Custom output filename
            
        Returns:
            Dictionary containing function result
        """
        try:
            print(f"🔄 Calling function: {function_name}")
            
            # Execute function call
            if parameters:
                result = self.conn.call(function_name, **parameters)
            else:
                result = self.conn.call(function_name)
            
            print(f"✅ Function executed successfully")
            
            # Save result if requested
            if save_result or output_file:
                filename = output_file or f"{function_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                self.save_result(result, filename)
            
            return result
            
        except Exception as e:
            print(f"❌ Error calling function {function_name}: {str(e)}")
            return {}
    
    def call_bapi(self, business_object: str, method: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute BAPI (Business Application Programming Interface)
        
        Common BAPIs:
        - BAPI_CUSTOMER_GETDETAIL2
        - BAPI_MATERIAL_GET_DETAIL  
        - BAPI_SALESORDER_GETSTATUS
        - BAPI_VENDOR_GETDETAIL
        """
        bapi_name = f"BAPI_{business_object.upper()}_{method.upper()}"
        return self.call_function(bapi_name, parameters)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get SAP system information"""
        try:
            # Get basic system info
            result = self.call_function('RFC_SYSTEM_INFO')
            
            # Get additional details
            system_info = {
                'system_info': result,
                'current_user': self.call_function('SUSR_USER_ADDR_READ', 
                                                  {'BNAME': self.conn.get_connection_attributes()['user']}),
                'server_time': self.call_function('GET_SYSTEM_DATETIME')
            }
            
            return system_info
            
        except Exception as e:
            print(f"❌ Error getting system info: {str(e)}")
            return {}
    
    def test_connection(self) -> bool:
        """Test SAP connection with simple RFC call"""
        try:
            result = self.call_function('RFC_PING')
            return True
        except Exception as e:
            print(f"❌ Connection test failed: {str(e)}")
            return False
    
    def list_available_functions(self, pattern: str = "*") -> list:
        """List available RFC function modules matching pattern"""
        try:
            result = self.call_function('RFC_FUNCTION_SEARCH',
                                      {'PATTERN': pattern,
                                       'FUNCNAME': '',
                                       'GROUPNAME': '',
                                       'LANGUAGE': 'EN'})
            
            functions = []
            if 'FUNCTIONS' in result:
                for func in result['FUNCTIONS']:
                    functions.append({
                        'name': func.get('FUNCNAME', ''),
                        'group': func.get('GROUPNAME', ''),
                        'text': func.get('TEXT', '')
                    })
            
            return functions
            
        except Exception as e:
            print(f"❌ Error listing functions: {str(e)}")
            return []
    
    def save_result(self, result: Dict[str, Any], filename: str):
        """Save function result to JSON file"""
        try:
            # Convert datetime objects to strings for JSON serialization
            def serialize_datetime(obj):
                if hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                return str(obj)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=serialize_datetime, ensure_ascii=False)
            
            print(f"✅ Result saved to {filename}")
            
        except Exception as e:
            print(f"❌ Error saving result: {str(e)}")
    
    def format_result(self, result: Dict[str, Any], compact: bool = False) -> str:
        """Format function result for display"""
        try:
            if compact:
                return json.dumps(result, indent=2, default=str, ensure_ascii=False)
            else:
                return pprint.pformat(result, width=120)
                
        except Exception as e:
            return f"Error formatting result: {str(e)}"
    
    def close_connection(self):
        """Clean up SAP connection"""
        try:
            self.conn.close()
            print("✅ SAP connection closed")
        except:
            pass

def load_function_templates() -> Dict[str, Dict[str, Any]]:
    """Load predefined function call templates for common operations"""
    return {
        'customer_details': {
            'function': 'BAPI_CUSTOMER_GETDETAIL2',
            'description': 'Get customer master data details',
            'parameters': {
                'CUSTOMERNO': '0000001000'  # Example customer number
            }
        },
        'material_details': {
            'function': 'BAPI_MATERIAL_GET_DETAIL',
            'description': 'Get material master data',
            'parameters': {
                'MATERIAL': '000000000000000001',  # Example material
                'PLANT': '1000'
            }
        },
        'sales_order_status': {
            'function': 'BAPI_SALESORDER_GETSTATUS',
            'description': 'Get sales order status',
            'parameters': {
                'SALESDOCUMENT': '0000000001'  # Example sales order
            }
        },
        'user_info': {
            'function': 'SUSR_USER_ADDR_READ',
            'description': 'Get user address information',
            'parameters': {
                'BNAME': 'USER_NAME'  # Will be replaced with current user
            }
        },
        'company_code_info': {
            'function': 'BAPI_COMPANYCODE_GETDETAIL',
            'description': 'Get company code details',
            'parameters': {
                'COMPANYCODEID': '1000'  # Example company code
            }
        }
    }

def main():
    """Main execution function with command-line interface"""
    if len(sys.argv) < 2:
        print("SAP RFC Function Caller")
        print("\nUsage:")
        print("  python rfc_function_caller.py <config_file> [function_name] [param_file]")
        print("  python rfc_function_caller.py <config_file> --interactive")
        print("  python rfc_function_caller.py <config_file> --template <template_name>")
        print("\nExamples:")
        print("  python rfc_function_caller.py sap_config.json RFC_SYSTEM_INFO")
        print("  python rfc_function_caller.py sap_config.json BAPI_CUSTOMER_GETDETAIL2 params.json")
        print("  python rfc_function_caller.py sap_config.json --interactive")
        print("  python rfc_function_caller.py sap_config.json --template customer_details")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    # Load configuration
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Error loading config: {str(e)}")
        sys.exit(1)
    
    # Initialize RFC caller
    caller = SAPRFCCaller(config)
    
    try:
        # Test connection first
        if not caller.test_connection():
            print("❌ Connection test failed")
            sys.exit(1)
        
        # Handle different execution modes
        if len(sys.argv) > 2 and sys.argv[2] == '--interactive':
            # Interactive mode
            print("\n🔧 SAP RFC Function Caller - Interactive Mode")
            print("Available commands:")
            print("  call <function_name> - Call function without parameters")
            print("  interface <function_name> - Show function interface")
            print("  system - Show system information")
            print("  search <pattern> - Search for functions")
            print("  templates - Show available templates")
            print("  template <name> - Execute template")
            print("  quit - Exit")
            
            templates = load_function_templates()
            
            while True:
                command = input("\n> ").strip().split()
                
                if not command:
                    continue
                
                if command[0] == 'quit':
                    break
                elif command[0] == 'call' and len(command) > 1:
                    result = caller.call_function(command[1])
                    if result:
                        print("\n📋 Result:")
                        print(caller.format_result(result, compact=True))
                elif command[0] == 'interface' and len(command) > 1:
                    interface = caller.get_function_interface(command[1])
                    if interface:
                        print(json.dumps(interface, indent=2))
                elif command[0] == 'system':
                    info = caller.get_system_info()
                    print(caller.format_result(info, compact=True))
                elif command[0] == 'search' and len(command) > 1:
                    functions = caller.list_available_functions(command[1])
                    for func in functions[:20]:  # Limit to first 20 results
                        print(f"  {func['name']} - {func['text']}")
                    if len(functions) > 20:
                        print(f"  ... and {len(functions) - 20} more")
                elif command[0] == 'templates':
                    print("\nAvailable templates:")
                    for name, template in templates.items():
                        print(f"  {name}: {template['description']}")
                elif command[0] == 'template' and len(command) > 1:
                    template_name = command[1]
                    if template_name in templates:
                        template = templates[template_name]
                        params = template['parameters'].copy()
                        
                        # Replace placeholders
                        if 'BNAME' in params and params['BNAME'] == 'USER_NAME':
                            params['BNAME'] = config['user']
                        
                        result = caller.call_function(template['function'], params)
                        if result:
                            print(f"\n📋 {template['description']} Result:")
                            print(caller.format_result(result, compact=True))
                    else:
                        print(f"❌ Template '{template_name}' not found")
                else:
                    print("❌ Invalid command")
                    
        elif len(sys.argv) > 2 and sys.argv[2] == '--template':
            # Template mode
            if len(sys.argv) < 4:
                print("❌ Template name required")
                sys.exit(1)
                
            template_name = sys.argv[3]
            templates = load_function_templates()
            
            if template_name not in templates:
                print(f"❌ Template '{template_name}' not found")
                print("Available templates:", list(templates.keys()))
                sys.exit(1)
            
            template = templates[template_name]
            params = template['parameters'].copy()
            
            # Replace placeholders
            if 'BNAME' in params and params['BNAME'] == 'USER_NAME':
                params['BNAME'] = config['user']
            
            result = caller.call_function(template['function'], params, save_result=True)
            if result:
                print(f"\n📋 {template['description']} Result:")
                print(caller.format_result(result))
                
        else:
            # Direct function call mode
            function_name = sys.argv[2]
            parameters = {}
            
            # Load parameters from file if provided
            if len(sys.argv) > 3:
                try:
                    with open(sys.argv[3], 'r') as f:
                        parameters = json.load(f)
                except Exception as e:
                    print(f"❌ Error loading parameters: {str(e)}")
                    sys.exit(1)
            
            # Execute function
            result = caller.call_function(function_name, parameters, save_result=True)
            
            if result:
                print(f"\n📋 Function Result:")
                print(caller.format_result(result))
    
    finally:
        caller.close_connection()

if __name__ == "__main__":
    main()