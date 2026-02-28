"""
Groq-powered Website Generator
Uses Groq API with open-source models to generate dynamic websites
"""

import os
import json
import base64
from typing import Dict, Any
import groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GroqWebsiteGenerator:
    def __init__(self):
        """Initialize Groq client"""
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables. Please set it in your .env file.")
        
        # Initialize Groq client
        self.client = groq.Groq(api_key=self.api_key)
        
        # Model configuration - using open-source model
        self.model = "mixtral-8x7b-32768"
        
        print(f"🤖 Initializing Groq Website Generator with model: {self.model}")
        print(f"✅ Groq client initialized successfully")
    
    def generate_site_plan(self, brief: Dict) -> Dict:
        """Generate site plan using Groq API"""
        business_name = brief.get('business_name', 'Your Business')
        industry = brief.get('industry', 'Technology')
        pages = brief.get('pages', ['home', 'about', 'services', 'contact'])
        tone = brief.get('tone', 'modern')
        features = brief.get('features', [])
        
        prompt = f'''Generate a detailed website structure for a business with the following details:

Business Name: {business_name}
Industry: {industry}
Pages to include: {', '.join(pages)}
Design Tone: {tone}
Key Features: {', '.join(features) if features else 'None specified'}

Create a comprehensive site plan with:
1. For each page, list the sections and their content
2. Generate engaging copy for headlines and descriptions
3. Suggest color scheme based on the industry and tone
4. Include call-to-action buttons and their text
5. Add testimonials or social proof sections if appropriate

Return the response in JSON format with the following structure:
{{
    "business_name": "{business_name}",
    "industry": "{industry}",
    "tone": "{tone}",
    "color_suggestions": {{
        "primary": "#hex",
        "secondary": "#hex",
        "accent": "#hex"
    }},
    "pages": [
        {{
            "name": "home",
            "title": "Page title",
            "sections": [
                {{
                    "type": "hero",
                    "content": {{
                        "headline": "Main headline",
                        "subheadline": "Supporting text",
                        "cta_text": "Button text"
                    }}
                }},
                {{
                    "type": "features",
                    "content": {{
                        "items": [
                            {{"title": "Feature 1", "description": "Description"}},
                            {{"title": "Feature 2", "description": "Description"}}
                        ]
                    }}
                }}
            ]
        }}
    ],
    "global_components": {{
        "header": {{
            "logo_text": "{business_name}",
            "menu_items": ["Home", "About", "Services", "Contact"]
        }},
        "footer": {{
            "copyright": "© 2024 {business_name}. All rights reserved.",
            "social_links": ["twitter", "linkedin", "facebook"]
        }}
    }}
}}

Make the content creative, engaging, and tailored to the {industry} industry with a {tone} tone.'''
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert web designer and copywriter. Generate detailed, creative website structures in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
            )
            
            content = response.choices[0].message.content
            # Try to extract JSON from the response
            try:
                if '```json' in content:
                    json_str = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    json_str = content.split('```')[1].split('```')[0].strip()
                else:
                    json_str = content
                
                result = json.loads(json_str)
                print(f"✅ Site plan generated successfully")
                return result
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing JSON response: {e}")
                return self.generate_fallback_site_plan(brief)
            
        except Exception as e:
            print(f"❌ Error generating site plan: {e}")
            return self.generate_fallback_site_plan(brief)
    
    def generate_html(self, site_plan: Dict, brief: Dict) -> str:
        """Generate HTML using Groq API"""
        business_name = site_plan.get('business_name', brief.get('business_name', 'Your Business'))
        industry = brief.get('industry', 'Technology')
        colors = brief.get('colors', site_plan.get('color_suggestions', {
            'primary': '#3B82F6',
            'secondary': '#10B981',
            'accent': '#F59E0B'
        }))
        
        site_plan_json = json.dumps(site_plan, indent=2)
        
        prompt = f'''Generate a complete, modern HTML5 website based on the following site plan:

Site Plan:
{site_plan_json}

Brand Colors:
- Primary: {colors.get('primary', '#3B82F6')}
- Secondary: {colors.get('secondary', '#10B981')}
- Accent: {colors.get('accent', '#F59E0B')}

Requirements:
1. Create a responsive design using Tailwind CSS (include CDN link)
2. Implement all sections from the site plan
3. Use the provided brand colors throughout
4. Add smooth scrolling and modern animations
5. Include a mobile-friendly navigation menu
6. Make it visually appealing for the {industry} industry
7. Include placeholder images with Font Awesome icons or SVG placeholders
8. Add interactive elements where appropriate

Generate a complete HTML file with embedded CSS and JavaScript. Include:
- Tailwind CSS CDN in the head
- Font Awesome for icons (CDN link)
- Custom CSS for animations and overrides
- JavaScript for interactivity (mobile menu, smooth scroll, etc.)
- Proper meta tags for SEO
- Favicon placeholder

Return only the HTML code without any explanations or markdown formatting.'''
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert frontend developer. Generate clean, modern HTML5 code with Tailwind CSS and Font Awesome icons."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=8000
            )
            
            html = response.choices[0].message.content
            html = html.replace('```html', '').replace('```', '').strip()
            
            print(f"✅ HTML generated successfully ({len(html)} characters)")
            return html
            
        except Exception as e:
            print(f"❌ Error generating HTML: {e}")
            return self.generate_fallback_html(site_plan, brief)
    
    def generate_fallback_site_plan(self, brief: Dict) -> Dict:
        """Enhanced fallback template-based site plan"""
        business_name = brief.get('business_name', 'Your Business')
        industry = brief.get('industry', 'Technology')
        pages = brief.get('pages', ['home', 'about', 'services', 'contact'])
        tone = brief.get('tone', 'modern')
        
        industry_content = {
            'Technology': {
                'features': [
                    {"title": "Cutting-Edge Solutions", "description": "Leverage the latest technology to stay ahead of the competition"},
                    {"title": "Expert Development Team", "description": "Our skilled developers create robust, scalable applications"},
                    {"title": "24/7 Technical Support", "description": "Round-the-clock assistance for your critical systems"}
                ],
                'hero_subheadline': "Innovative technology solutions for modern businesses"
            },
            'Education': {
                'features': [
                    {"title": "Expert Instructors", "description": "Learn from industry professionals with years of experience"},
                    {"title": "Flexible Learning", "description": "Self-paced courses that fit your schedule"},
                    {"title": "Hands-on Projects", "description": "Build real-world projects to showcase your skills"}
                ],
                'hero_subheadline': "Transform your future with quality education"
            },
            'E-commerce': {
                'features': [
                    {"title": "Secure Payments", "description": "Multiple payment options with bank-level security"},
                    {"title": "Fast Shipping", "description": "Quick delivery to your doorstep"},
                    {"title": "24/7 Customer Service", "description": "Always here to help with your orders"}
                ],
                'hero_subheadline': "Shop the best products at amazing prices"
            }
        }
        
        content = industry_content.get(industry, {
            'features': [
                {"title": "Quality Service", "description": "We provide top-quality services tailored to your needs"},
                {"title": "Expert Team", "description": "Our experienced team ensures the best results"},
                {"title": "24/7 Support", "description": "We're always here to help you succeed"}
            ],
            'hero_subheadline': f"Leading {industry} solutions for your business"
        })
        
        return {
            "business_name": business_name,
            "industry": industry,
            "tone": tone,
            "color_suggestions": {
                "primary": brief.get('colors', {}).get('primary', '#3B82F6'),
                "secondary": brief.get('colors', {}).get('secondary', '#10B981'),
                "accent": brief.get('colors', {}).get('accent', '#F59E0B')
            },
            "pages": [
                {
                    "name": "home",
                    "title": f"{business_name} - Home",
                    "sections": [
                        {
                            "type": "hero",
                            "content": {
                                "headline": f"Welcome to {business_name}",
                                "subheadline": content['hero_subheadline'],
                                "cta_text": "Get Started"
                            }
                        },
                        {
                            "type": "features",
                            "content": {
                                "items": content['features']
                            }
                        },
                        {
                            "type": "about",
                            "content": {
                                "headline": "About Us",
                                "paragraph": f"{business_name} is a leading {industry} company dedicated to providing exceptional solutions and services to our clients."
                            }
                        }
                    ]
                },
                {
                    "name": "services",
                    "title": f"{business_name} - Services",
                    "sections": [
                        {
                            "type": "services",
                            "content": {
                                "items": content['features']
                            }
                        }
                    ]
                },
                {
                    "name": "contact",
                    "title": f"{business_name} - Contact",
                    "sections": [
                        {
                            "type": "contact",
                            "content": {
                                "email": "info@example.com",
                                "phone": "+1 (555) 123-4567",
                                "address": "123 Business St, City, State 12345"
                            }
                        }
                    ]
                }
            ]
        }
    
    def generate_fallback_html(self, site_plan: Dict, brief: Dict) -> str:
        """Enhanced fallback template-based HTML"""
        business_name = site_plan.get('business_name', brief.get('business_name', 'Your Business'))
        industry = brief.get('industry', 'Technology')
        colors = brief.get('colors', site_plan.get('color_suggestions', {
            'primary': '#3B82F6',
            'secondary': '#10B981',
            'accent': '#F59E0B'
        }))
        
        features_html = ""
        for page in site_plan.get('pages', []):
            for section in page.get('sections', []):
                if section.get('type') == 'features':
                    items = section.get('content', {}).get('items', [])
                    for item in items:
                        features_html += f'''
            <div class="bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow">
                <h3 class="text-xl font-semibold mb-2" style="color: {colors['primary']}">{item.get('title', 'Feature')}</h3>
                <p class="text-gray-600">{item.get('description', 'Description')}</p>
            </div>'''
        
        if not features_html:
            features_html = f'''
            <div class="bg-white p-6 rounded-lg shadow-lg">
                <h3 class="text-xl font-semibold mb-2" style="color: {colors['primary']}">Quality Service</h3>
                <p class="text-gray-600">We provide top-quality services tailored to your needs</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow-lg">
                <h3 class="text-xl font-semibold mb-2" style="color: {colors['primary']}">Expert Team</h3>
                <p class="text-gray-600">Our experienced team ensures the best results</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow-lg">
                <h3 class="text-xl font-semibold mb-2" style="color: {colors['primary']}">24/7 Support</h3>
                <p class="text-gray-600">We're always here to help you succeed</p>
            </div>'''
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{business_name} - {industry} Solutions</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body {{ font-family: 'Inter', sans-serif; }}
        :root {{
            --primary: {colors['primary']};
            --secondary: {colors['secondary']};
            --accent: {colors['accent']};
        }}
        .bg-primary {{ background-color: var(--primary); }}
        .text-primary {{ color: var(--primary); }}
        .hover-scale:hover {{ transform: scale(1.05); transition: transform 0.3s; }}
        .animate-fade-in {{
            animation: fadeIn 1s ease-in;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body class="bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-lg sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <div class="flex items-center">
                    <span class="text-xl font-bold" style="color: var(--primary)">{business_name}</span>
                </div>
                <div class="hidden md:flex items-center space-x-8">
                    <a href="#home" class="text-gray-700 hover:text-gray-900 transition">Home</a>
                    <a href="#about" class="text-gray-700 hover:text-gray-900 transition">About</a>
                    <a href="#services" class="text-gray-700 hover:text-gray-900 transition">Services</a>
                    <a href="#contact" class="text-gray-700 hover:text-gray-900 transition">Contact</a>
                </div>
                <div class="md:hidden">
                    <button id="mobile-menu-button" class="text-gray-700">
                        <i class="fas fa-bars text-2xl"></i>
                    </button>
                </div>
            </div>
        </div>
        <!-- Mobile menu -->
        <div id="mobile-menu" class="hidden md:hidden bg-white border-t">
            <div class="px-4 py-2 space-y-2">
                <a href="#home" class="block text-gray-700 hover:text-gray-900 py-2">Home</a>
                <a href="#about" class="block text-gray-700 hover:text-gray-900 py-2">About</a>
                <a href="#services" class="block text-gray-700 hover:text-gray-900 py-2">Services</a>
                <a href="#contact" class="block text-gray-700 hover:text-gray-900 py-2">Contact</a>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section id="home" class="py-20 animate-fade-in" style="background: linear-gradient(135deg, var(--primary), var(--secondary))">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 class="text-5xl md:text-6xl font-bold text-white mb-6">Welcome to {business_name}</h1>
            <p class="text-xl text-white opacity-90 mb-8 max-w-2xl mx-auto">
                {industry} solutions tailored to your needs
            </p>
            <button class="bg-white px-8 py-3 rounded-lg font-semibold hover-scale" style="color: var(--primary)">
                Get Started <i class="fas fa-arrow-right ml-2"></i>
            </button>
        </div>
    </section>

    <!-- Features Section -->
    <section id="services" class="py-20 bg-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 class="text-3xl font-bold text-center mb-12">Our Services</h2>
            <div class="grid md:grid-cols-3 gap-8">
                {features_html}
            </div>
        </div>
    </section>

    <!-- About Section -->
    <section id="about" class="py-20 bg-gray-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid md:grid-cols-2 gap-12 items-center">
                <div>
                    <h2 class="text-3xl font-bold mb-6" style="color: var(--primary)">About Us</h2>
                    <p class="text-gray-600 mb-6">
                        {business_name} is a leading {industry} company dedicated to providing exceptional solutions and services to our clients. 
                        With years of experience and a team of experts, we deliver results that exceed expectations.
                    </p>
                    <button class="px-6 py-2 text-white rounded-lg" style="background-color: var(--primary)">
                        Learn More <i class="fas fa-arrow-right ml-2"></i>
                    </button>
                </div>
                <div class="bg-gray-200 h-96 rounded-lg flex items-center justify-center">
                    <i class="fas fa-building text-6xl text-gray-400"></i>
                </div>
            </div>
        </div>
    </section>

    <!-- Contact Section -->
    <section id="contact" class="py-20 bg-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 class="text-3xl font-bold text-center mb-12">Contact Us</h2>
            <div class="grid md:grid-cols-2 gap-12">
                <div>
                    <form class="space-y-4">
                        <input type="text" placeholder="Your Name" 
                               class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2" 
                               style="focus:ring-color: {colors['primary']}">
                        <input type="email" placeholder="Your Email" 
                               class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2"
                               style="focus:ring-color: {colors['primary']}">
                        <textarea placeholder="Your Message" rows="4" 
                                  class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2"
                                  style="focus:ring-color: {colors['primary']}"></textarea>
                        <button class="px-6 py-2 text-white rounded-lg hover-scale" 
                                style="background-color: var(--primary)">
                            Send Message <i class="fas fa-paper-plane ml-2"></i>
                        </button>
                    </form>
                </div>
                <div>
                    <h3 class="text-xl font-semibold mb-4">Contact Information</h3>
                    <ul class="space-y-4 text-gray-600">
                        <li class="flex items-center">
                            <i class="fas fa-envelope w-6" style="color: var(--primary)"></i>
                            <span class="ml-3">info@{business_name.lower().replace(' ', '')}.com</span>
                        </li>
                        <li class="flex items-center">
                            <i class="fas fa-phone w-6" style="color: var(--primary)"></i>
                            <span class="ml-3">+1 (555) 123-4567</span>
                        </li>
                        <li class="flex items-center">
                            <i class="fas fa-map-marker-alt w-6" style="color: var(--primary)"></i>
                            <span class="ml-3">123 Business St, City, State 12345</span>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-12">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center">
                <p>&copy; 2024 {business_name}. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script>
        // Mobile menu toggle
        const mobileMenuButton = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        
        if (mobileMenuButton && mobileMenu) {{
            mobileMenuButton.addEventListener('click', () => {{
                mobileMenu.classList.toggle('hidden');
            }});
        }}

        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                    if (mobileMenu && !mobileMenu.classList.contains('hidden')) {{
                        mobileMenu.classList.add('hidden');
                    }}
                }}
            }});
        }});

        // Form submission (prevent default for demo)
        document.querySelectorAll('form').forEach(form => {{
            form.addEventListener('submit', (e) => {{
                e.preventDefault();
                alert('Thank you for your message! (Demo)');
            }});
        }});
    </script>
</body>
</html>'''
    
    def generate_website(self, project_id: str, brief: Dict) -> Dict:
        """Generate complete website using Groq API"""
        print(f"🎨 Generating website with Groq for project {project_id}")
        print(f"📋 Brief: {brief.get('business_name')} - {brief.get('industry')}")
        
        try:
            # Step 1: Generate site plan
            print("📝 Generating site plan...")
            site_plan = self.generate_site_plan(brief)
            
            # Step 2: Generate HTML
            print("🔧 Generating HTML...")
            html = self.generate_html(site_plan, brief)
            
            # Create data URL for preview
            html_bytes = html.encode('utf-8')
            base64_html = base64.b64encode(html_bytes).decode('utf-8')
            data_url = f"data:text/html;charset=utf-8;base64,{base64_html}"
            
            print(f"✅ Website generated successfully for project {project_id}")
            
            return {
                'project_id': project_id,
                'preview_url': data_url,
                'html': html,
                'site_plan': site_plan,
                'model_used': self.model
            }
            
        except Exception as e:
            print(f"❌ Error generating website: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to template-based generation
            return self.generate_fallback_website(project_id, brief)
    
    def generate_fallback_website(self, project_id: str, brief: Dict) -> Dict:
        """Fallback website generation when API fails"""
        print("📝 Using fallback template generation...")
        site_plan = self.generate_fallback_site_plan(brief)
        html = self.generate_fallback_html(site_plan, brief)
        
        html_bytes = html.encode('utf-8')
        base64_html = base64.b64encode(html_bytes).decode('utf-8')
        data_url = f"data:text/html;charset=utf-8;base64,{base64_html}"
        
        return {
            'project_id': project_id,
            'preview_url': data_url,
            'html': html,
            'site_plan': site_plan,
            'model_used': 'fallback-template'
        }

# Create singleton instance
generator = None

def get_generator():
    """Get or create the Groq generator singleton"""
    global generator
    if generator is None:
        generator = GroqWebsiteGenerator()
    return generator

def generate_website(project_id: str, brief: Dict) -> Dict:
    """Convenience function to generate website using Groq"""
    return get_generator().generate_website(project_id, brief)