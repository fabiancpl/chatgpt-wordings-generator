import json

import streamlit as st
from annotated_text import annotated_text

import openai


def main():
    st.set_page_config(page_title="Remarketing Demo")

    st.title("Remarketing Demo")

    st.markdown("*Todos los campos del formulario son opcionales con excepción del país y la temperatura. ChatGPT podrá agregar wildcards si lo considera en caso de que no se provea información.*")
    
    site_opts = ["Argentina", "Brasil", "Colombia", "México", "Perú", "Chile", "Uruguay"]
    site = st.selectbox("País:", site_opts)

    # User data
    st.subheader("Datos del usuario")

    user_name = st.text_input("Nombre del usuario:", "")

    genre_opts = ["", "Femenino", "Masculino", "LGBTQ+"]
    genre = st.selectbox("Género:", genre_opts)

    age_opts = ["", "18-29", "30-42", "43-54", "55-74"]
    age = st.selectbox("Rango de edad:", age_opts)

    # Product data
    st.subheader("Datos del producto")

    item_category = st.text_input("Categorías del producto (separadas por coma):", "")
    
    item_title = st.text_input("Título del producto:", "")

    interaction_opts = ["", "Visitado", "Recomendado"]
    interaction = st.selectbox("¿Visitado o recomendado?", interaction_opts)

    # Purchase conditions
    st.subheader("Condiciones de compra")

    best_seller = st.checkbox("Más vendido")

    fast_shipping = st.checkbox("Llega mañana")

    free_return = st.checkbox("Devolución gratis")

    installments = st.checkbox("Cuotas sin interés")

    discount = st.checkbox("Descuento del 25%")

    # Model parameters

    temperature = st.number_input("Temperatura:", step=0.1, value=0.8)

    if st.button("Crear wording"):
        response = generate_response(site,
                                     user_name, genre, age,
                                     item_category, item_title, interaction,
                                     best_seller, fast_shipping, free_return, installments, discount,
                                     temperature)
        response_dict = json.loads(response)

        title = response_dict["title"] = response_dict["title"]
        subtitle = response_dict["subtitle"] = response_dict["subtitle"]

        # Render the response in a light panel
        with st.container():
            st.markdown(f"**{title}**", unsafe_allow_html=True)
            st.markdown(f"{subtitle}", unsafe_allow_html=True)
            annotated_text([i for i in [ 
                (site, "País"),
                (user_name, "Usuario") if user_name != "" else None,
                (genre, "Género") if genre != "" else None,
                (age, "Rango de edad") if age != "" else None,
                (item_category, "Categorías del producto") if item_category != "" else None,
                (item_title, "Título del producto") if item_title != "" else None,
                (interaction, "¿Visitado o Recomendado?") if item_title != "" else None,
                ("Si", "Más vendido") if best_seller else None,
                ("Si", "Llega mañana") if fast_shipping else None,
                ("Si", "Devolución gratis") if free_return else None,
                ("Si", "Cuotas sin interés") if installments else None,
                ("Si", "Descuento del 25%") if discount else None,
                (str(temperature), "Temperatura")
            ] if i is not None])


def generate_response(site,
                      user_name, genre, age,
                      item_category, item_title, interaction,
                      best_seller, fast_shipping, free_return, installments, discount,
                      temperature):

    content = f"""
    - Nombre del usuario: {user_name}
    - Género del usuario: {genre}
    - Rango etario: {age}
    - Categorías del producto: {item_category}
    - Título del producto: {item_title}
    - Visitado o recomendado: {interaction}
    - Condiciones de compra: {"Más vendido" if best_seller else ""}, {"Llega mañana" if fast_shipping else ""}, {"Devolución gratis" if free_return else ""}, {"Cuotas sin interés" if installments else ""}, {"Descuento del 25%" if discount else ""}
    """

    prompt = f"""
    Como un experto en marketing digital, tu labor es ayudarme a crear wordings para el envío de campañas de marketing cuyo objetivo es motivar al usuario a finalizar la compra de un producto previamente visitado en nuestro marketplace.

    También puede suceder que el usuario no haya visitado el producto, pero se le esté recomendando uno similar utilizando nuestro algoritmo de recomendación.

    El wording debe ser lo más engage posible, por lo que siempre que se pueda trata de inferir características del producto que sean llamativas para el usuario dada su edad o género.

    También debes tener en cuenta que el público objetivo es de {site}, por lo que siempre que se pueda trata de utilizar expresiones propias de ese país. Note que para Brasil el wording debe estar en portugués.

    No olvides que el usuario puede comprar el producto para sí mismo o para alguien más. Infiere estos detalles basado en el típo de producto y las características del usuario. Ajusta el wording en consecuencia.

    Los wordings deben ser cortos y estar compuestos de un título y subtítulo. El título no debe superar los 35 caracteres y el subtítulo los 150 caracteres.

    Devuélveme el wording en formato JSON el cual debe tener 2 claves: title, subtitle.

    Ahora te voy a pasar en comillas triples los detalles del usuario y el producto a considerar dentro del wording, además de posibles condiciones de compra. La información proporcionada tiene la siguiente estructura:

    - Nombre del usuario
    - Género del usuario (Femenino, Masculino, LGBTQ+)
    - Rango etario (también se detalla la generación a la que pertenece el usuario)
    - Categorías del producto (organizadas por niveles separadas por comas)
    - Título del producto
    - Visitado o recomendado (indica si el usuario visitó el producto o es un producto recomendado por el algoritmo de recomendación)
    - Condiciones de compra (separadas por comas)



    '''{content}'''

    Responde solo con el archivo JSON.

    Un ejemplo de wording para el producto 'Vaso Termico De Acero Con Tapa Para Cafe Bebidas Frio Calor' podría ser el siguiente: 
    - title: ¡Oye, Francisco! Dale toda la onda a tus bebidas con estilo, 
    - subtitle: 'Vasos térmicos de acero ¡Ideal para tu café en casa u oficina!
    """

    # Make an API call to ChatGPT to generate a response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            { "role": "system", "content": "Experto en marketing digital" },
            { "role": "user", "content": prompt }
        ],
        temperature=temperature
    )

    return response["choices"][0]["message"]["content"]

if __name__ == "__main__":
    main()