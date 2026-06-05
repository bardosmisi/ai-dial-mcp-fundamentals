from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

from models.user_info import UserSearchRequest, UserCreate, UserUpdate
from user_client import UserClient

mcp = FastMCP(
    name="users-management-mcp-server",
    host="0.0.0.0",
    port=8005,
)
user_client = UserClient()


# ==================== TOOLS ====================

@mcp.tool(description="Get a user by their unique ID. Returns full user profile.")
async def get_user_by_id(user_id: int) -> str:
    return await user_client.get_user(user_id)


@mcp.tool(description="Delete a user by their unique ID. Returns confirmation message.")
async def delete_user(user_id: int) -> str:
    return await user_client.delete_user(user_id)


@mcp.tool(description="Search users by optional filters: name, surname, email, gender. All fields support partial matching except gender (exact match).")
async def search_user(
    name: Optional[str] = None,
    surname: Optional[str] = None,
    email: Optional[str] = None,
    gender: Optional[str] = None,
) -> str:
    return await user_client.search_users(name=name, surname=surname, email=email, gender=gender)


@mcp.tool(description="Add a new user to the system. Requires name, surname, email, and about_me. Returns confirmation with created user data.")
async def add_user(
    name: str,
    surname: str,
    email: str,
    about_me: str,
    phone: Optional[str] = None,
    date_of_birth: Optional[str] = None,
    gender: Optional[str] = None,
    company: Optional[str] = None,
    salary: Optional[float] = None,
) -> str:
    user = UserCreate(
        name=name,
        surname=surname,
        email=email,
        about_me=about_me,
        phone=phone,
        date_of_birth=date_of_birth,
        gender=gender,
        company=company,
        salary=salary,
    )
    return await user_client.add_user(user)


@mcp.tool(description="Update an existing user by ID. All fields are optional — only provided fields will be updated.")
async def update_user(
    user_id: int,
    name: Optional[str] = None,
    surname: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    date_of_birth: Optional[str] = None,
    gender: Optional[str] = None,
    company: Optional[str] = None,
    salary: Optional[float] = None,
) -> str:
    update = UserUpdate(
        name=name,
        surname=surname,
        email=email,
        phone=phone,
        date_of_birth=date_of_birth,
        gender=gender,
        company=company,
        salary=salary,
    )
    return await user_client.update_user(user_id, update)


# ==================== MCP RESOURCES ====================

@mcp.resource(
    uri="users-management://flow-diagram",
    mime_type="image/png",
    description="Flow diagram showing the Users Management Service Swagger endpoints and architecture."
)
async def get_flow_diagram() -> bytes:
    image_path = Path(__file__).parent / "flow.png"
    return image_path.read_bytes()


# ==================== MCP PROMPTS ====================

SEARCH_PROMPT = """
You are helping users search through a dynamic user database. The database contains 
realistic synthetic user profiles with the following searchable fields:

## Available Search Parameters
- **name**: First name (partial matching, case-insensitive)
- **surname**: Last name (partial matching, case-insensitive)  
- **email**: Email address (partial matching, case-insensitive)
- **gender**: Exact match (male, female, other, prefer_not_to_say)

## Search Strategy Guidance

### For Name Searches
- Use partial names: "john" finds John, Johnny, Johnson, etc.
- Try common variations: "mike" vs "michael", "liz" vs "elizabeth"
- Consider cultural name variations

### For Email Searches  
- Search by domain: "gmail" for all Gmail users
- Search by name patterns: "john" for emails containing john
- Use company names to find business emails

### For Demographic Analysis
- Combine gender with other criteria for targeted searches
- Use broad searches first, then narrow down

### Effective Search Combinations
- Name + Gender: Find specific demographic segments
- Email domain + Surname: Find business contacts
- Partial names: Cast wider nets for common names

## Example Search Patterns
```
"Find all Johns" → name="john"
"Gmail users named Smith" → email="gmail" + surname="smith"  
"Female users with company emails" → gender="female" + email="company"
"Users with Johnson surname" → surname="johnson"
```

## Tips for Better Results
1. Start broad, then narrow down
2. Try variations of names (John vs Johnny)
3. Use partial matches creatively
4. Combine multiple criteria for precision
5. Remember searches are case-insensitive

When helping users search, suggest multiple search strategies and explain 
why certain approaches might be more effective for their goals.
"""

CREATE_PROMPT = """
You are helping create realistic user profiles for the system. Follow these guidelines 
to ensure data consistency and realism.

## Required Fields
- **name**: 2-50 characters, letters only, culturally appropriate
- **surname**: 2-50 characters, letters only  
- **email**: Valid format, must be unique in system
- **about_me**: Rich, realistic biography (see guidelines below)

## Optional Fields Best Practices
- **phone**: Use E.164 format (+1234567890) when possible
- **date_of_birth**: YYYY-MM-DD format, realistic ages (18-80)
- **gender**: Use standard values (male, female, other, prefer_not_to_say)
- **company**: Real-sounding company names
- **salary**: $30,000-$200,000 range for employed individuals

## Address Guidelines
Provide complete, realistic addresses:
- **country**: Full country names
- **city**: Actual city names  
- **street**: Realistic street addresses
- **flat_house**: Apartment/unit format (Apt 123, Unit 5B, Suite 200)

## Credit Card Guidelines  
Generate realistic but non-functional card data:
- **num**: 16 digits formatted as XXXX-XXXX-XXXX-XXXX
- **cvv**: 3 digits (000-999)
- **exp_date**: MM/YYYY format, future dates only

## Biography Creation ("about_me")
Create engaging, realistic biographies that include:

### Personality Elements
- 1-3 personality traits (curious, adventurous, analytical, etc.)
- Authentic voice and writing style
- Cultural and demographic appropriateness

### Interests & Hobbies  
- 2-4 specific hobbies or activities
- 1-3 broader interests or passion areas
- 1-2 life goals or aspirations

### Biography Templates
Use varied narrative structures:
- "I'm a [trait] person who loves [hobbies]..."
- "When I'm not working, you can find me [activity]..."  
- "Life is all about balance for me. I enjoy [interests]..."
- "As someone who's [trait], I find great joy in [hobby]..."

## Data Validation Reminders
- Email uniqueness is enforced (check existing users)
- Phone numbers should follow consistent formatting
- Date formats must be exact (YYYY-MM-DD)
- Credit card expiration dates must be in the future
- Salary values should be realistic for the demographic

## Cultural Sensitivity
- Match names to appropriate cultural backgrounds
- Consider regional variations in address formats
- Use realistic company names for the user's location
- Ensure hobbies and interests are culturally appropriate

When creating profiles, aim for diversity in:
- Geographic representation
- Age distribution  
- Interest variety
- Socioeconomic backgrounds
- Cultural backgrounds
"""


@mcp.prompt(description="Helps users formulate effective search queries for the user database.")
async def search_guidance() -> str:
    return SEARCH_PROMPT


@mcp.prompt(description="Guides creation of realistic and consistent user profiles.")
async def create_user_guidance() -> str:
    return CREATE_PROMPT


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
