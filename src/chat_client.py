from openai import OpenAI
from textwrap import dedent
from typing import Dict, List, Tuple


class ChatClient:
    """
    A comprehensive class for generating various advertising content including text responses,
    hashtags, taglines, campaign lines, product advantages, and video prompts.

    Attributes:
        api_key (str): The API key for accessing the chat service.
        api_url (str): The base URL for the chat API.
    """

    def __init__(self, api_key: str, api_url: str):
        """
        Initializes the AdvertisingContentGenerator with API credentials.

        Args:
            api_key (str): The API key to authenticate the chat service.
            api_url (str): The base URL of the chat API.
        """
        self.client = OpenAI(base_url=api_url, api_key=api_key)

    def generate_response(
        self, product_name: str, description: str, base64_image: str
    ) -> str:
        """
        Generates a text response using product details and an image.

        Args:
            product_name (str): The name of the product.
            description (str): A description of the product.
            base64_image (str): The base64 encoded image of the product.

        Returns:
            str: The generated text response based on the provided details.
        """
        response = self.client.chat.completions.create(
            model="aria",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                        {
                            "type": "text",
                            "text": dedent(
                                f"""
                        <image>
                        Product Name: {product_name}
                        Description: {description}

                        Create an engaging product description that highlights its unique features,
                        benefits, and emotional appeal. Focus on creating a compelling narrative
                        that resonates with the target audience.
                        """
                            ),
                        },
                    ],
                }
            ],
            stream=False,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stop=["<|im_end|>"],
        )
        return response.choices[0].message.content

    def generate_taglines(
        self, product_name: str, description: str, target_audience: str
    ) -> List[str]:
        """
        Generates creative taglines for the product.

        Args:
            product_name (str): The name of the product.
            description (str): A description of the product.
            target_audience (str): Description of the target audience.

        Returns:
            List[str]: A list of generated taglines.
        """
        tagline_prompt = dedent(
            f"""
            Product: {product_name}
            Description: {description}
            Target Audience: {target_audience}

            Generate exactly 5 powerful, memorable taglines for this product that:
            1. Are concise (2-8 words)
            2. Highlight unique selling propositions
            3. Have emotional appeal
            4. Are easy to remember
            5. Align with the target audience

            Format: Return only the taglines, one per line.
            """
        )

        response = self.client.chat.completions.create(
            model="aria",
            messages=[{"role": "user", "content": tagline_prompt}],
            temperature=0.8,
            max_tokens=256,
            top_p=1,
        )
        return response.choices[0].message.content.strip().split("\n")

    def generate_campaign_lines(
        self,
        product_name: str,
        description: str,
        target_audience: str,
        campaign_theme: str,
    ) -> List[str]:
        """
        Generates campaign lines based on a specific theme.

        Args:
            product_name (str): The name of the product.
            description (str): A description of the product.
            target_audience (str): Description of the target audience.
            campaign_theme (str): The theme or focus of the campaign.

        Returns:
            List[str]: A list of campaign lines.
        """
        campaign_prompt = dedent(
            f"""
            Product: {product_name}
            Description: {description}
            Target Audience: {target_audience}
            Campaign Theme: {campaign_theme}

            Generate exactly 3 compelling campaign lines that:
            1. Align with the campaign theme
            2. Resonate with the target audience
            3. Communicate the core message effectively
            4. Are memorable and shareable
            5. Maintain brand voice and positioning

            Format: Return only the campaign lines, one per line.
            """
        )

        response = self.client.chat.completions.create(
            model="aria",
            messages=[{"role": "user", "content": campaign_prompt}],
            temperature=0.7,
            max_tokens=256,
            top_p=1,
        )
        return response.choices[0].message.content.strip().split("\n")

    def generate_product_advantages(
        self, product_name: str, description: str
    ) -> List[str]:
        """
        Generates a list of product advantages and benefits.

        Args:
            product_name (str): The name of the product.
            description (str): A description of the product.

        Returns:
            List[str]: A list of product advantages.
        """
        advantages_prompt = dedent(
            f"""
            Product: {product_name}
            Description: {description}

            Generate exactly 5 clear, specific advantages of this product that:
            1. Focus on unique selling propositions
            2. Highlight tangible benefits
            3. Address customer pain points
            4. Differentiate from competitors
            5. Are specific and measurable where possible

            Format: Return only the advantages, one per line, starting with a dash (-).
            """
        )

        response = self.client.chat.completions.create(
            model="aria",
            messages=[{"role": "user", "content": advantages_prompt}],
            temperature=0.6,
            max_tokens=256,
            top_p=1,
        )
        return [
            adv.strip("- ")
            for adv in response.choices[0].message.content.strip().split("\n")
        ]

    def generate_video_prompt(
        self, product_name: str, description: str, mood: str, style: str
    ) -> str:
        """
        Generates a prompt for AI video generation (6-second limitation).

        Args:
            product_name (str): The name of the product.
            description (str): A description of the product.
            mood (str): The desired mood of the video.
            style (str): The visual style for the video.

        Returns:
            str: A detailed video generation prompt.
        """
        video_prompt = dedent(
            f"""
            Generate a 6-second video prompt for {product_name}.

            Key Details:
            - Product: {product_name}
            - Description: {description}
            - Mood: {mood}
            - Style: {style}

            Create a prompt that:
            1. Works within 6-second limitation
            2. Uses abstract/general visuals (due to diffusion model limitations)
            3. Focuses on mood and atmosphere
            4. Creates emotional connection
            5. Maintains visual continuity
            6. Uses simple, clear scenes. Use As less scenes as possible, preferably 1-2 scenes.
            7. Avoids complex text or specific products

            Format the response as a detailed but concise scene description.
            """
        )

        response = self.client.chat.completions.create(
            model="aria",
            messages=[{"role": "user", "content": video_prompt}],
            temperature=0.7,
            max_tokens=256,
            top_p=1,
        )
        return response.choices[0].message.content.strip()

    def generate_hashtags(self, product_name: str, description: str) -> List[str]:
        """
        Generates hashtags relevant to the product name and description.

        Args:
            product_name (str): The name of the product.
            description (str): A description of the product.

        Returns:
            List[str]: A list of generated hashtags.
        """
        hashtag_prompt = dedent(
            f"""
            Product: {product_name}
            Description: {description}

            Generate exactly 10 relevant, trending hashtags that:
            1. Are specific to the product category
            2. Include both broad and niche tags
            3. Mix branded and general hashtags
            4. Are currently popular on social media
            5. Are relevant to the target audience

            Format: Return only the hashtags, one per line, including the # symbol.
            """
        )

        response = self.client.chat.completions.create(
            model="aria",
            messages=[{"role": "user", "content": hashtag_prompt}],
            temperature=0.6,
            max_tokens=256,
            top_p=1,
        )
        return response.choices[0].message.content.strip().split("\n")
