#!/usr/bin/env python3
"""
Automated CTF Challenge Triage System v2.0

Enhanced with:
- Complexity detection (hybrid challenges, restrictive constraints)
- Better warnings without solution bias
- Continuous documentation prompts

Usage: python3 triage.py <challenge_path>
"""

import subprocess
import time
import os
import sys
import json
import statistics
from pathlib import Path

class CTFTriage:
    def __init__(self, target_path):
        self.target = target_path
        self.results = {
            'target': target_path,
            'file_info': {},
            'timing_analysis': {},
            'crash_analysis': {},
            'string_analysis': {},
            'behavioral_analysis': {},
            'complexity_indicators': {},
            'classification': 'UNKNOWN',
            'confidence': 0.0,
            'recommended_approach': '',
            'recommended_tools': [],
            'warnings': []
        }
    
    def run_command(self, cmd, timeout=5, input_data=None):
        """Execute command and return output safely"""
        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=isinstance(cmd, str)
            )
            stdout, stderr = proc.communicate(
                input=input_data.encode() if input_data else None,
                timeout=timeout
            )
            return {
                'returncode': proc.returncode,
                'stdout': stdout.decode('utf-8', errors='ignore'),
                'stderr': stderr.decode('utf-8', errors='ignore'),
                'success': True
            }
        except subprocess.TimeoutExpired:
            proc.kill()
            return {'success': False, 'error': 'timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def analyze_file_info(self):
        """Get basic file information"""
        print("[*] Analyzing file information...")
        
        # File type
        result = self.run_command(['file', self.target])
        if result['success']:
            self.results['file_info']['type'] = result['stdout'].strip()
        
        # File size
        size = os.path.getsize(self.target)
        self.results['file_info']['size'] = size
        self.results['file_info']['size_human'] = self._human_size(size)
        
        # Permissions
        stat = os.stat(self.target)
        self.results['file_info']['executable'] = bool(stat.st_mode & 0o111)
        
        print(f"    Type: {self.results['file_info'].get('type', 'Unknown')}")
        print(f"    Size: {self.results['file_info']['size_human']}")
        print(f"    Executable: {self.results['file_info']['executable']}")
    
    def analyze_strings(self):
        """Extract and analyze strings from binary"""
        print("[*] Analyzing strings...")
        
        result = self.run_command(['strings', self.target])
        if not result['success']:
            return
        
        strings = result['stdout'].split('\n')
        self.results['string_analysis']['count'] = len(strings)
        
        # Look for interesting patterns
        interesting = {
            'flags': [],
            'success_msgs': [],
            'fail_msgs': [],
            'crypto_hints': [],
            'network_hints': [],
            'constraint_hints': [],
            'web_framework_hints': []
        }
        
        for s in strings:
            s_lower = s.lower()
            if 'flag{' in s_lower or 'ctf{' in s_lower:
                interesting['flags'].append(s)
            if any(word in s_lower for word in ['success', 'correct', 'granted', 'win']):
                interesting['success_msgs'].append(s)
            if any(word in s_lower for word in ['fail', 'wrong', 'denied', 'try again']):
                interesting['fail_msgs'].append(s)
            if any(word in s_lower for word in ['rsa', 'aes', 'encrypt', 'decrypt', 'cipher', 'key', 'prime']):
                interesting['crypto_hints'].append(s)
            if any(word in s_lower for word in ['http', 'socket', 'port', 'server', 'client', 'url']):
                interesting['network_hints'].append(s)
            if any(word in s_lower for word in ['charset', 'filter', 'restricted', 'allowed', 'blacklist', 'jail']):
                interesting['constraint_hints'].append(s)
            if any(word in s_lower for word in ['flask', 'django', 'secret_key', 'session', 'jwt', 'express', 'app.secret']):
                interesting['web_framework_hints'].append(s)
        
        self.results['string_analysis']['interesting'] = interesting
        
        print(f"    Total strings: {len(strings)}")
        print(f"    Success messages: {len(interesting['success_msgs'])}")
        print(f"    Fail messages: {len(interesting['fail_msgs'])}")
        print(f"    Crypto hints: {len(interesting['crypto_hints'])}")
        if interesting['constraint_hints']:
            print(f"    Warning: Constraint hints: {len(interesting['constraint_hints'])}")
        if interesting['web_framework_hints']:
            print(f"    Web framework hints: {len(interesting['web_framework_hints'])}")
    
    def analyze_timing(self, num_samples=10):
        """Test for timing side-channels"""
        print("[*] Analyzing timing characteristics...")
        
        if not self.results['file_info'].get('executable'):
            print("    Skipping (not executable)")
            return
        
        test_inputs = [
            "0" * 8,
            "1" * 8,
            "2" * 8,
            "3" * 8,
            "4" * 8,
            "5" * 8,
            "test1234",
            "aaaaaaaa",
            "12345678",
            "99999999"
        ]
        
        times = []
        for test_input in test_inputs[:num_samples]:
            start = time.time()
            result = self.run_command([self.target], timeout=3, input_data=test_input)
            elapsed = time.time() - start
            
            if result['success']:
                times.append(elapsed)
        
        if len(times) < 3:
            print("    Insufficient data")
            return
        
        avg_time = statistics.mean(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        min_time = min(times)
        max_time = max(times)
        variance_pct = (std_dev / avg_time * 100) if avg_time > 0 else 0
        
        self.results['timing_analysis'] = {
            'avg_time': avg_time,
            'std_dev': std_dev,
            'min_time': min_time,
            'max_time': max_time,
            'variance_pct': variance_pct,
            'samples': times
        }
        
        print(f"    Average time: {avg_time:.4f}s")
        print(f"    Std deviation: {std_dev:.4f}s")
        print(f"    Variance: {variance_pct:.2f}%")
        
        if variance_pct > 15:
            # Additional validation: check if variance correlates with input
            # Run same input multiple times - should have low variance if real timing attack
            same_input_times = []
            test_input = "12345678"
            for _ in range(5):
                start = time.time()
                result = self.run_command([self.target], timeout=3, input_data=test_input)
                if result['success']:
                    same_input_times.append(time.time() - start)
            
            if len(same_input_times) >= 3:
                same_input_variance = (statistics.stdev(same_input_times) / statistics.mean(same_input_times) * 100)
                
                if same_input_variance < 10:
                    # Low variance on same input = likely real timing attack
                    print(f"    Warning: SIGNIFICANT TIMING VARIANCE DETECTED!")
                    print(f"    Warning: Same-input variance: {same_input_variance:.2f}% (confirms timing attack)")
                else:
                    # High variance even on same input = probably just noise
                    print(f"    Warning: Timing variance detected but likely noise ({same_input_variance:.2f}% on repeated input)")
                    self.results['timing_analysis']['likely_noise'] = True
    
    def analyze_crashes(self):
        """Test for crash/memory corruption vulnerabilities"""
        print("[*] Analyzing crash behavior...")
        
        if not self.results['file_info'].get('executable'):
            print("    Skipping (not executable)")
            return
        
        test_cases = {
            'long_input': "A" * 1000,
            'very_long': "A" * 10000,
            'format_string': "%s%s%s%s%s%s%s%s",
            'format_x': "%x" * 20,
            'null_bytes': "test\x00\x00\x00",
            'newlines': "\n" * 100,
            'special_chars': "!@#$%^&*()"
        }
        
        crashes = {}
        for name, test_input in test_cases.items():
            result = self.run_command([self.target], timeout=2, input_data=test_input)
            
            if not result['success']:
                crashes[name] = 'timeout/error'
            elif result['returncode'] < 0:
                crashes[name] = f'signal_{abs(result["returncode"])}'
            elif 'segmentation fault' in result['stderr'].lower():
                crashes[name] = 'segfault'
        
        self.results['crash_analysis'] = crashes
        
        if crashes:
            print(f"    Warning: CRASHES DETECTED: {len(crashes)} test cases")
            for name, crash_type in crashes.items():
                print(f"        {name}: {crash_type}")
        else:
            print("    No crashes detected")
    
    def analyze_behavior(self):
        """Analyze behavioral patterns"""
        print("[*] Analyzing behavioral patterns...")
        
        if not self.results['file_info'].get('executable'):
            print("    Skipping (not executable)")
            return
        
        # Test with standard input
        test_inputs = ["test", "admin", "password", "12345678"]
        outputs = []
        
        for inp in test_inputs:
            result = self.run_command([self.target], timeout=2, input_data=inp)
            if result['success']:
                outputs.append(result['stdout'])
        
        # Check if outputs vary
        unique_outputs = len(set(outputs))
        
        self.results['behavioral_analysis'] = {
            'output_variance': unique_outputs > 1,
            'accepts_input': len(outputs) > 0,
            'sample_outputs': outputs[:3]
        }
        
        print(f"    Accepts input: {self.results['behavioral_analysis']['accepts_input']}")
        print(f"    Output varies: {self.results['behavioral_analysis']['output_variance']}")
    
    def detect_complexity_indicators(self):
        """Detect indicators of challenge complexity without biasing solution"""
        print("[*] Detecting complexity indicators...")
        
        indicators = {
            'multiple_categories': False,
            'has_constraints': False,
            'advanced_likely': False,
            'warnings': []
        }
        
        # Check for multiple challenge categories
        categories = []
        if self.results['string_analysis'].get('interesting', {}).get('crypto_hints'):
            categories.append('crypto')
        if self.results['crash_analysis']:
            categories.append('pwn')
        if self.results['string_analysis'].get('interesting', {}).get('network_hints'):
            categories.append('web')
        if self.results.get('timing_analysis', {}).get('variance_pct', 0) > 15:
            categories.append('timing')
        
        if len(categories) >= 2:
            indicators['multiple_categories'] = True
            indicators['warnings'].append(
                f"Multi-category challenge: {' + '.join(categories)}. May require solving multiple stages."
            )
        
        # Check for restrictive constraints
        if self.results['string_analysis'].get('interesting', {}).get('constraint_hints'):
            indicators['has_constraints'] = True
            indicators['warnings'].append(
                "Detected input restrictions. May need creative workarounds or bypasses."
            )
        
        # Try to read file content for deeper analysis
        try:
            with open(self.target, 'r', errors='ignore') as f:
                file_content = f.read().lower()
            
            # Look for advanced technique hints (without being prescriptive)
            advanced_patterns = {
                'padding oracle': ['padding', 'oracle'],
                'related messages': ['related', 'message'],
                'lattice': ['lattice'],
                'polynomial': ['polynomial', 'coppersmith'],
            }
            
            found_advanced = []
            for technique, patterns in advanced_patterns.items():
                if all(p in file_content for p in patterns):
                    found_advanced.append(technique)
            
            if found_advanced:
                indicators['advanced_likely'] = True
                indicators['warnings'].append(
                    f"May involve advanced techniques. Research before attempting."
                )
        
        except:
            pass
        
        self.results['complexity_indicators'] = indicators
        
        if indicators['warnings']:
            print(f"    Complexity warnings: {len(indicators['warnings'])}")
        else:
            print(f"    No special complexity indicators detected")
        
        return indicators
    
    def analyze_python_scripts(self):
        """Analyze Python scripts for crypto patterns"""
        if not self.target.endswith('.py'):
            return
        
        print("[*] Analyzing Python script...")
        
        try:
            with open(self.target, 'r') as f:
                content = f.read()
            
            # Check for crypto patterns
            crypto_indicators = {
                'rsa': ['pow(', 'from_bytes', 'e =', 'n =', 'p =', 'q ='],
                'aes': ['AES', 'Crypto.Cipher', 'encrypt', 'decrypt'],
                'encoding': ['base64', 'b64encode', 'b64decode'],
            }
            
            detected = []
            for crypto_type, patterns in crypto_indicators.items():
                if sum(1 for p in patterns if p in content) >= 2:
                    detected.append(crypto_type)
            
            if detected:
                self.results['string_analysis']['crypto_type'] = detected
                print(f"    Crypto patterns detected: {', '.join(detected)}")
        
        except Exception as e:
            print(f"    Error analyzing script: {e}")
    
    def classify(self):
        """Classify challenge based on all analysis"""
        print("\n[*] Classifying challenge...")
        
        confidence = 0.0
        classification = "UNKNOWN"
        approach = ""
        tools = []
        
        # Detect complexity
        complexity = self.detect_complexity_indicators()
        
        # Check for Python crypto scripts FIRST
        if self.target.endswith('.py') and 'crypto_type' in self.results.get('string_analysis', {}):
            classification = "CRYPTOGRAPHY"
            confidence = 0.9
            crypto_types = ', '.join(self.results['string_analysis']['crypto_type'])
            approach = f"Python cryptography: Analyze script, identify weakness, apply appropriate attack"
            tools = ['python3', 'sympy', 'gmpy2']
        
        # Check for timing attack
        timing = self.results.get('timing_analysis', {})
        if timing.get('variance_pct', 0) > 15 and not timing.get('likely_noise', False):
            classification = "TIMING_SIDE_CHANNEL"
            confidence = min(timing['variance_pct'] / 20, 1.0)
            approach = "Timing side-channel: Measure execution time to extract information"
            tools = ['custom_timing_script', 'python3']
        
        # Check for memory corruption
        elif self.results['crash_analysis']:
            classification = "MEMORY_CORRUPTION"
            confidence = min(len(self.results['crash_analysis']) / 3, 1.0)
            approach = "Memory exploitation: Identify vulnerability type, calculate offsets, write exploit"
            tools = ['gdb', 'pwntools', 'ghidra']
        
        # Check for crypto
        elif self.results['string_analysis'].get('interesting', {}).get('crypto_hints'):
            classification = "CRYPTOGRAPHY"
            confidence = 0.7
            approach = "Cryptographic challenge: Identify algorithm, find weakness, apply attack"
            tools = ['python3', 'sympy', 'gmpy2']
        
        
        # Check for web frameworks (specific detection before general web)
        elif self.results['string_analysis'].get('interesting', {}).get('web_framework_hints'):
            classification = "WEB_FRAMEWORK"
            confidence = 0.8
            approach = "Web framework security: Check for exposed secrets (secret_key), session manipulation, SSTI, deserialization"
            tools = ['python3', 'flask-unsign', 'requests', 'burp']
        
        # Check for web
        elif self.results['string_analysis'].get('interesting', {}).get('network_hints'):
            classification = "WEB_NETWORK"
            confidence = 0.6
            approach = "Web/network exploitation: Scan, test common vulnerabilities, analyze source"
            tools = ['secops_tools', 'burp', 'curl']
        
        # Check file type for specific hints
        elif 'Java' in self.results['file_info'].get('type', ''):
            classification = "JAVA_REVERSING"
            confidence = 0.8
            approach = "Java reverse engineering: Decompile, analyze logic, extract/compute flag"
            tools = ['jd-gui', 'jadx', 'ghidra']
        
        # Default to logic-based reversing if executable
        elif self.results['file_info'].get('executable'):
            classification = "LOGIC_REVERSING"
            confidence = 0.5
            approach = "Logic analysis: Use symbolic execution, dynamic analysis, or manual reversing"
            tools = ['angr', 'ghidra', 'gdb']
        
        # Modify for hybrid challenges
        if complexity['multiple_categories']:
            classification += "_HYBRID"
            confidence *= 0.7  # Lower confidence for hybrid
            approach = "Hybrid challenge: " + approach
        
        self.results['classification'] = classification
        self.results['confidence'] = confidence
        self.results['recommended_approach'] = approach
        self.results['recommended_tools'] = tools
        
        print(f"\n{'='*60}")
        print(f"CLASSIFICATION: {classification}")
        print(f"CONFIDENCE: {confidence*100:.1f}%")
        print(f"\nRECOMMENDED APPROACH:")
        print(f"  {approach}")
        print(f"\nSUGGESTED TOOLS:")
        print(f"  {', '.join(tools)}")
        
        # Print complexity warnings
        if complexity['warnings']:
            print(f"\nWarning: COMPLEXITY WARNINGS:")
            for warning in complexity['warnings']:
                print(f"  - {warning}")
        
        print(f"\nCRITICAL REMINDERS:")
        print(f"  - Read ALL source code completely (Phase 0)")
        print(f"  - Validate assumptions frequently")
        print(f"  - Create PROGRESS.md to track discoveries")
        print(f"  - Pause after 5-7 tool calls to reassess")
        
        print(f"{'='*60}\n")
    
    def _human_size(self, size):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    
    def run_full_analysis(self):
        """Run complete triage analysis"""
        print(f"\n{'='*60}")
        print(f"CTF CHALLENGE TRIAGE v2.0")
        print(f"Target: {self.target}")
        print(f"{'='*60}\n")
        
        self.analyze_file_info()
        self.analyze_python_scripts()
        self.analyze_strings()
        self.analyze_timing()
        self.analyze_crashes()
        self.analyze_behavior()
        self.classify()
        
        return self.results
    
    def save_report(self, output_path=None):
        """Save analysis report to JSON"""
        if output_path is None:
            output_path = f"{self.target}_triage.json"
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"[+] Report saved to: {output_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 triage.py <challenge_path>")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if not os.path.exists(target):
        print(f"Error: {target} does not exist")
        sys.exit(1)
    
    triage = CTFTriage(target)
    results = triage.run_full_analysis()
    
    # Save report
    triage.save_report()
    
    print("\n[*] NEXT STEPS:")
    print(f"    1. Read AUTONOMOUS_SOLVER_README.md Phase 0 section")
    print(f"    2. Understand the challenge completely before attacking")
    print(f"    3. Follow attack template for: {results['classification']}")
    print(f"    4. Document progress continuously in PROGRESS.md")

if __name__ == '__main__':
    main()
