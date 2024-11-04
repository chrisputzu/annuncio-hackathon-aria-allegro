# ![Annuncio Logo](annuncio_logo_svg.svg) 

# 📢 Annuncio

Annuncio is a multimodal application designed to generate product advertisements using the power of Aria and Allegro AI models. It allows users to create detailed product descriptions and promotional videos seamlessly, integrating Streamlit as the web framework and providing an easy-to-use API for interaction.

## 🚀 Features

- **Product Data Generation**: Utilize the Aria model to generate comprehensive product description based on input parameters such as product name, description and image.
- **Video Generation**: Create promotional videos using the Allegro model based on the generated product data.
- **Hashtag Generation**: Utilize the Aria model to generate hashtags based on product name and description product.

## 🛠️ Installation

To get started with Annuncio, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/chrisputzu/annuncio-hackathon-aria-allegro
   cd annuncio
   ```

2. **Install the required dependencies**: 
   
   Create a virtual environment and install the dependencies.

    ```bash
    pip install -r requirements.txt
    ```

3. **Set up environment variables**: 
   
   Create a .env file in the root directory of the project and add your ARIA and ALLEGRO API keys:
    ```bash
    ARIA_API_KEY=your_aria_api_key
    ALLEGRO_API_KEY=your_allegro_api_key
    ```

## 💻 Usage
To run the application with streamlit, execute the following command:

```bash
streamlit run app.py
```

The application will start on http://localhost:8503/.

## 🎉 Contributing
We welcome contributions! Feel free to open issues, submit pull requests, and provide feedback.

## 📄 License
This project is licensed under the MIT License.

