import os
import base64
import time
import streamlit as st
from dotenv import load_dotenv
from src.video_generator import VideoGenerator
from src.chat_client import ChatClient
from src.finishing import add_text_overlay


def display_content_section(title: str, content, type="text"):
    """Helper function to display content sections with consistent styling"""
    st.write(f"**{title}:**")
    if isinstance(content, list):
        for item in content:
            st.write(f"• {item}".replace("<|im_end|>", ""))
    elif type == "code":
        st.code(content)
    else:
        st.write(content.replace("<|im_end|>", ""))
    st.write("---")


def main():
    """
    Enhanced Streamlit application for generating comprehensive advertising content
    including video, taglines, campaign lines, product advantages, and hashtags.
    """
    # Load environment variables and initialize generators
    load_dotenv()
    api_key = os.getenv("ARIA_API_KEY")
    bearer_token = os.getenv("ALLEGRO_API_KEY")
    api_url = "https://api.rhymes.ai/v1"

    video_generator = VideoGenerator(bearer_token, api_url)
    ad_generator = ChatClient(api_key, api_url)

    # Set up the Streamlit interface
    st.title("Annuncio")
    st.subheader("Let AI handle your Product Advertisement!")

    # Initialize session state for tracking steps if not exists
    if "step" not in st.session_state:
        st.session_state.step = 1
    # Step 1: Basic Product Information
    st.header("Step 1: Basic Product Information")
    uploaded_file = st.file_uploader(
        "1. Upload Product Image", type=["jpg", "jpeg", "png"]
    )
    product_name = st.text_input("2. Enter Product Name:")
    description = st.text_area("3. Enter Product Description:")

    # Next button for Step 1
    if st.button("Next →" if st.session_state.step == 1 else "←"):
        if st.session_state.step == 1:
            if uploaded_file and product_name and description:
                st.session_state.step = 2
            else:
                st.error("Please complete all fields in Step 1 before proceeding.")
        else:
            st.session_state.step = 1
        st.rerun()

    # Step 2: Campaign Settings (only show if Step 1 is complete)
    if st.session_state.step == 2:

        st.header("Step 2: Campaign Settings")
        target_audience = st.text_area(
            "Target Audience Description:",
            help="Describe your ideal customer demographics, interests, and behaviors",
        )
        campaign_theme = st.text_input(
            "Campaign Theme:", help="Enter the main theme or message of your campaign"
        )
        mood = st.selectbox(
            "Video Mood:",
            [
                "Energetic",
                "Professional",
                "Luxurious",
                "Friendly",
                "Technical",
                "Emotional",
            ],
        )
        style = st.selectbox(
            "Visual Style:",
            ["Modern", "Classic", "Minimalist", "Bold", "Natural", "Tech-focused"],
        )

        # Generate Content button (only show in Step 2)
        if st.button("Generate Content"):
            if target_audience and campaign_theme:
                with st.spinner("Generating advertising content..."):
                    # Convert image to base64
                    image_bytes = uploaded_file.read()
                    base64_image = base64.b64encode(image_bytes).decode("utf-8")

                    # Create placeholder containers for content
                    video_placeholder = st.empty()
                    video_placeholder.info(
                        "🎥 Video advertisement is being generated... This may take a few minutes."
                    )

                    # Generate all content in parallel
                    col1, col2 = st.columns(2)

                    with col1:
                        # Generate and display description
                        description_response = ad_generator.generate_response(
                            product_name, description, base64_image
                        )
                        display_content_section(
                            "Product Description", description_response
                        )

                        # Generate and display taglines
                        taglines = ad_generator.generate_taglines(
                            product_name, description, target_audience
                        )
                        display_content_section("Taglines", taglines)

                    with col2:
                        # Generate and display campaign lines
                        campaign_lines = ad_generator.generate_campaign_lines(
                            product_name, description, target_audience, campaign_theme
                        )
                        display_content_section("Campaign Lines", campaign_lines)

                        # Generate and display product advantages
                        advantages = ad_generator.generate_product_advantages(
                            product_name, description
                        )
                        display_content_section("Product Advantages", advantages)

                        # Generate and display hashtags
                        hashtags = ad_generator.generate_hashtags(
                            product_name, description
                        )
                        display_content_section("Hashtags", hashtags)

                    # Generate video prompt
                    video_prompt = ad_generator.generate_video_prompt(
                        product_name, description, mood, style
                    )
                    video_response = video_generator.generate_video(video_prompt)
                    request_id = video_response.get("data")

                    # Poll for video completion
                    max_attempts = 60
                    attempts = 0
                    video_link = None

                    while attempts < max_attempts:
                        video_data = video_generator.query_video_status(request_id)
                        video_link = video_data.get("data")

                        if video_link:
                            print(video_link)
                            video_placeholder.info("🎨 Adding text overlay to video...")

                            # Add text overlay to video
                            final_video_path = add_text_overlay(
                                video_link, product_name
                            )
                            print("Final Video Path:", final_video_path)
                            if final_video_path:
                                video_placeholder.success(
                                    "✨ Video processing complete! Scroll to End"
                                )
                                # Store the path in session state
                                st.session_state.final_video_path = final_video_path

                                # Display the final video
                                with open(final_video_path, "rb") as video_file:
                                    video_bytes = video_file.read()
                                    st.video(video_bytes)

                                # Display the prompt used for video generation
                                with st.expander("View Video Generation Prompt"):
                                    st.code(video_prompt)
                            else:
                                video_placeholder.error(
                                    "❌ Error adding text overlay to video."
                                )
                            break

                        attempts += 1
                        time.sleep(5)
                        video_placeholder.info(
                            f"🎥 Video generation in progress... (Attempt {attempts}/{max_attempts})"
                        )

                    if not video_link:
                        video_placeholder.error(
                            "❌ Video generation timed out. Please try again."
                        )

                    # Add download buttons for content
                    st.download_button(
                        label="Download Content as Text",
                        data=f"""
                        Product: {product_name}
                        
                        Description:
                        {description_response}
                        
                        Taglines:
                        {chr(10).join(taglines)}
                        
                        Campaign Lines:
                        {chr(10).join(campaign_lines)}
                        
                        Product Advantages:
                        {chr(10).join(advantages)}
                        
                        Hashtags:
                        {chr(10).join(hashtags)}
                        
                        Video Prompt:
                        {video_prompt}
                        
                        Video Link:
                        {video_link if video_link else 'Generation failed'}
                        """,
                        file_name=f"{product_name}_content.txt",
                        mime="text/plain",
                    )

            else:
                st.error(
                    "Please complete all fields in Step 2 before generating content."
                )


if __name__ == "__main__":
    main()
