@app.route("/llm-settings", methods=["GET", "POST"])
@login_required
def llm_settings():
    # Get available LLM providers and models
    available_providers = llm_selector.get_providers()
    
    # Get current user settings
    user_settings = {}
    if hasattr(current_user, 'id'):
        # TODO: Load user settings from database when implemented
        # For now, use session as temporary storage
        user_settings = session.get('user_settings', {})
    
    # Default settings if none exist
    if not user_settings:
        user_settings = {
            'llm_provider': 'inferless',     # Default to Inferless
            'llm_model': 'cb77-instruct-7b', # Default Inferless model
            'detail_level': 'medium',        # medium detail level
            'audience': 'technical',         # technical audience
            'documentation_style': 'formal', # formal style
            'tooltip_delay': 1000,           # 1000ms delay for tooltips
            'tooltip_x_offset': 10,          # 10px right offset
            'tooltip_y_offset': 10,          # 10px down offset
            'tooltip_font_size': 6,          # 6px font size
            'tooltip_opacity': 0.9           # 90% opacity
        }
        session['user_settings'] = user_settings

@app.route("/api/check-keys", methods=["GET"])
def check_api_keys():
    """Check if API keys are available and prompt user if needed"""
    # Get current provider from user settings or from query parameters
    provider = request.args.get('provider', None)
    
    if current_user.is_authenticated:
        user_settings = session.get('user_settings', {})
        if not provider:
            provider = user_settings.get('llm_provider', 'inferless')
    else:
        # For unauthenticated users, default to 'inferless' if not specified
        if not provider:
            provider = 'inferless'
    
    result = {
        "inferless": {"available": bool(os.environ.get('INFERLESS_API_KEY'))},
        "perplexity": {"available": bool(os.environ.get('PERPLEXITY_API_KEY'))},
        "groq": {"available": bool(os.environ.get('GROQ_API_KEY'))},
        "selected_provider": provider,
        "needs_key": False
    }
    
    # Check if the selected provider needs a key
    if provider == 'inferless' and not result["inferless"]["available"]:
        result["needs_key"] = True
    elif provider == 'perplexity' and not result["perplexity"]["available"]:
        result["needs_key"] = True
    elif provider == 'groq' and not result["groq"]["available"]:
        result["needs_key"] = True
    
    return jsonify(result)

@app.route("/api/save-keys", methods=["POST"])
def save_api_keys():
    # In production, you would save these keys securely
    # For simplicity, we'll save them in environment variables
    inferless_key = request.form.get('inferless_key')
    perplexity_key = request.form.get('perplexity_key')
    groq_key = request.form.get('groq_key')
    
    result = {
        "inferless": {"updated": False, "message": ""},
        "perplexity": {"updated": False, "message": ""},
        "groq": {"updated": False, "message": ""}
    }
    
    if inferless_key:
        # In a real app, you would store this securely
        # For demo, we'll set it in environment variables
        os.environ['INFERLESS_API_KEY'] = inferless_key
        result["inferless"]["updated"] = True
        result["inferless"]["message"] = "Inferless API key updated successfully"
        
        # For authenticated users, save the preference
        if current_user.is_authenticated:
            user_settings = session.get('user_settings', {})
            user_settings['has_inferless_key'] = True
            session['user_settings'] = user_settings
        
        # Reinitialize the LLM selector to recognize the new API key
        if "inferless" not in llm_selector.get_providers():
            llm_selector._initialize_providers()
    
    if perplexity_key:
        # In a real app, you would store this securely
        # For demo, we'll set it in environment variables
        os.environ['PERPLEXITY_API_KEY'] = perplexity_key
        result["perplexity"]["updated"] = True
        result["perplexity"]["message"] = "Perplexity API key updated successfully"
        
        # For authenticated users, save the preference
        if current_user.is_authenticated:
            user_settings = session.get('user_settings', {})
            user_settings['has_perplexity_key'] = True
            session['user_settings'] = user_settings
        
    if groq_key:
        # In a real app, you would store this securely
        # For demo, we'll set it in environment variables
        os.environ['GROQ_API_KEY'] = groq_key
        result["groq"]["updated"] = True
        result["groq"]["message"] = "Groq API key updated successfully"
        
        # For authenticated users, save the preference
        if current_user.is_authenticated:
            user_settings = session.get('user_settings', {})
            user_settings['has_groq_key'] = True
            session['user_settings'] = user_settings
        
        # Reinitialize the LLM selector to recognize the new API key
        if "groq" not in llm_selector.get_providers():
            llm_selector._initialize_providers()
    
    return jsonify(result) 