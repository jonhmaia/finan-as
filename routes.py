import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, send_file
import io
from app import app, db
from models import Entry
from datetime import datetime, date
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

@app.route('/')
def index():
    month = request.args.get('month')
    year = request.args.get('year')
    
    query = Entry.query
    
    if month and year:
        month = int(month)
        year = int(year)
        query = query.filter(db.extract('month', Entry.date) == month, db.extract('year', Entry.date) == year)

    entries = query.all()

    total_entradas = sum(entry.amount for entry in entries if entry.entry_type == 'Entrada')
    total_saidas = sum(entry.amount for entry in entries if entry.entry_type == 'Saída')
    saldo_final = total_entradas - total_saidas

    today = date.today()
    current_month = int(month) if month else today.month
    current_year = int(year) if year else today.year

    return render_template('index.html', entries=entries, total_entradas=total_entradas, total_saidas=total_saidas, saldo_final=saldo_final, current_month=current_month, current_year=current_year)

@app.route('/add', methods=['POST'])
def add_entry():
    if request.method == 'POST':
        date_str = request.form['date']
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        description = request.form['description']
        amount = float(request.form['amount'])
        category = request.form['category']
        entry_type = request.form['entry_type']
        new_entry = Entry(date=date, description=description, amount=amount, category=category, entry_type=entry_type)
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    entry = Entry.query.get(entry_id)
    if entry:
        db.session.delete(entry)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/download')
def download_entries():
    month = request.args.get('month')
    year = request.args.get('year')
    
    query = Entry.query
    
    if month and year:
        month = int(month)
        year = int(year)
        query = query.filter(db.extract('month', Entry.date) == month, db.extract('year', Entry.date) == year)

    entries = query.all()

    # Estruturar os dados de entradas e saídas por semana
    semanas = {'Semana 1': [], 'Semana 2': [], 'Semana 3': [], 'Semana 4': [], 'Semana 5': []}
    for entry in entries:
        semana = f"Semana {((entry.date.day - 1) // 7) + 1}"
        semanas[semana].append(entry.amount)

    # Preparar dados para o DataFrame
    data = {
        'FLUXO DE CAIXA MENSAL': ['Semana 1', 'Semana 2', 'Semana 3', 'Semana 4', 'Semana 5'],
        'Realizado': [sum(semanas['Semana 1']), sum(semanas['Semana 2']), sum(semanas['Semana 3']), sum(semanas['Semana 4']), sum(semanas['Semana 5'])],
    }

    df = pd.DataFrame(data)

    # Gerar o arquivo Excel em memória
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Despesas')
    output.seek(0)

    # Enviar o arquivo como resposta de download
    return send_file(output, as_attachment=True, download_name='despesas.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/download_pdf')
def download_pdf():
    month = request.args.get('month')
    year = request.args.get('year')
    query = Entry.query
    
    if month and year:
        month = int(month)
        year = int(year)
        query = query.filter(db.extract('month', Entry.date) == month, db.extract('year', Entry.date) == year)

    entries = query.all()

    # Gerar o arquivo PDF em memória
    output = io.BytesIO()
    c = canvas.Canvas(output, pagesize=letter)
    width, height = letter
    c.drawImage("data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBwgHBhMTBxIVFhIXGB0XGBgWFh0dFxsaGBcaHRkfHhshHigsGCAlHhcZIzEiMSkrNi8uFyszRDgtNygtLisBCgoKDg0OGxAQGy8mICUtLi0vLzgtLzcrNTU4ListKy0yNystLzUyKy0tLy0tKzcvLS0tLS0tLSswMC0tLS0tLf/AABEIAOEA4QMBEQACEQEDEQH/xAAcAAEAAgMBAQEAAAAAAAAAAAAABQYDBAcCAQj/xAA/EAACAQMCAwMJBQcDBQEAAAAAAQIDBBEFEgYhMUFRcQcTIjJSYYGRsWJygsHwFBYjQpKhsyZTc3Sy0dLiFf/EABsBAQADAQEBAQAAAAAAAAAAAAADBQYEAgEH/8QAMBEBAAEEAAQEBAYCAwAAAAAAAAECAwQRBRIhUSIxQYFxkbHRE2GhweHwMjMGFCP/2gAMAwEAAhEDEQA/AO4gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY61enQjmq8HNk5dnGp57tWo/vk9U0VVTqGvYanaX+f2eS3LrF8pL4fmMbLtZFO7c+3qlvY9y1/nHv6Nw6UAAAAAAAAAAAAAAAAAAAAAAAAAAAADzUqQpQbqNJLq2+R5qqimN1TqH2ImqdQhbriCnnFnz+0+nwXaZ3P45ybpx43PefL2WFrAq86/k0HWlXlmby/eY3Iu3btfPcmZl1RbiiNRCqXM50rpypNqSk2mnhrn3l3j1TTqY813bppqoiKo3Gk5pPGtSg1HVluj7cV6S8V2+K+TNHi8QnyufNWZXBYq8Vifb7LnZ3lvfUFO0mpxfan+sP3FtTVFUbhQXLVdqrlrjUs56RgAAAAAAAAAAAAAAAAAAAAAAAAA5FfcVVb3U6kL+WFCpKMfYxGTS5dj5dSnz8W7c6xO47NrjcOot2qarcdZiJnv5JKynO4mlQTk30S5meqxaqquWmNyhvRTRG6p0t2maJOKTvX+Ffmyzxf+P075sj5fdRZGbE9LfzautcJ0rnMtPe2XXa/Vf/qd1/hFE9bPSe3p/CXE4rVb8N3rHf1UTU7O5sa227g4y9/b4PtRwfhV255a400+Nft3qeaidounrdzo9Zz06bU+3HqvHZJdJL9ci2xbdcdfJ0XcS3kU8t2nf19ncLOpKtaQlPq4pvxaTLF+d1xy1TEd2YPIAAAAAAAAAAAAAAAAAAAAAAAAfnnVaE1rNfzmV/FnyfXnNvp2Hmaoh+kYnWxRMdo+iT4e4ivuH6ubNpwfrQl0fx6xfh8mRx0naLN4dZy6dV9J9J/vm6jw7xjpmuYjF+brf7c3zf3X0l9fcSxO2OzeFX8XrMbp7x+/ZIarrdjpaxcSzPshHnL5di97Ib2RRajdXyc+NhXcifBHTv6KjqmrT1uO24ilT7I//XXPhgzmZxC9XPh6RC9xsOMWeamfF3VbU+GKjpt6f6S9l+t8H2/rqS4vGqZmKL3Se/ouLPEqd6u9Pz9HYrCLjY01Lk1CP0RpI8mEuzuurXeWc+owAAAAAAAAAAAAAAAAAAAAADHXrUrei53ElGKWXKTSSXvb6H2mmap1EdTelK1HykWNG9UNPpurBP0p52r8Ka5+Lx+ZcWeC3a6d1zyz6R90UXYqq5YSFSjw5xva5WPOJdV6NaH/AJXzRXZOJcsTq5Hv6LHEz7+LO7c9O3ooXEnBWqaNmdFeeo+1Bekl9qPZ4rK8Dk5WswuM2cjw1eGr8/L2n7qruyuQ0t5WK2qym8zbbfVt5b8X2lRkU9ZctVERGoWfQtJvNRw6SxD25dPh7RxU4Fy/PTpHdTZmZas9Jnc9lwpW2naHQ3V5LPtS6v7qLbG4dYxvFrc95ZbO4lERzXatR2/vmjlxjbxvMVaclTfSXV+Lj3FjTqqOjO0cetzc1VTMU9/X5LFa3NC7oqVtJSi+1P8AWAu7d2i5TzUTuGYJAAAAAAAAAAAAAAAAAAAAAHKfK5XqvWqVNyls80pbc+juc5rOO/CXM0vBKKfw6qtdd+fsq8zJrtXYiI3GlJtE5Vy6mdJrWRaqjmp+SUt1VoVVKhJxkuacXhrwaIrk01Ry1RuCvLiF60HjetTShrK3L/civS/FHt8V8mUGVwyn/Kz8vsjp4hTE6qbutcHaLxLR89pslTqPnvp84Sf2o9/yZS10VUTqqNS0vD+N3LURqeaj++Uvug8FWemQ36rJVJLnjpTXwfrfHl7jnm1RHirT53G7l2OW34af1/j2SV/rqgttgvdua5LwXacV3iVEdLfX82VyM2fK3591drqrcVd1duUn2v8AXI4py5mdzKkuWa7lXNXO5RepqFGS39xZ8PrquxOnHftU2+tTY4Ou6n7xU4021GW7Kz1xCTWfiWtVvlp3KbhN2f8AtRTT0id/R0wgbEAAAAAAAAAAAAAAAAAAAAByDyvyxxLT/wCCP+Soabgn+mr4/tCtzLfNXHwaXkw21eLYxqJNOnNNPmmsdq7Sbi86xtx3h4xbWrm/ylfdZ4Jt6zctLxCXsP1H4ez/AHXgU1jiddPS51jv6vWVgTXG7U6nt6KZqNvLSqu2+i4y7u1+9d695bWapv8AWjyUVOHl3Lk2+XWvWfL+UjwBe1anEqjF4g4Syk+uFyz3kfFMemjH5vOdw0OFgU40b3MzPn2+S9a5GM5RUu7J+X/8iv3Ldy3FM9NT0+Sw/DouRqpE/skpSxBZ8Cls5FV2qKKY6z6OarD0krPQ11uv6V+bNNicJq/yvz7R+75TjU+qs+UaEKVzQVNJJQlyXijT4lummmYpjUKHj1MRVREdpRfBT/1NR/F/jkTXo8EuHhEay6ff6OqnC2oAAAAAAAAAAAAAAAAAAAADjXlllt4opf8ATx/yVDS8F/01fH9oeKrXN1aXkqqxXGVPc8ehNc+9rkibi0TONPxh8i3FE7l3IyiRzLymxzrsP+KP/fM0vBp1Zn4/tDmu3OWvTU8ncccUR+5P6E3F53je8JaK+ZfNfntrw8H9T8t4/b5q6PhP7PNy5yzDDpVTN9H4/RlXwm1y5tE/H6Skpu83RYjdvTn3lLknf0UuqhLPuy1g7sSNxLOcb1NdEflKJ4Kf+p6P4v8AHIlyI/8AOXHwunWVT7/R1crGvAAAAAAAAAAAAAAAAAAAAAcu8rPD1/fapC5owcqMaShLbzaanN811SxJc/oX/B8i3TTNuqdTMoMnJuWbf/nTue/Zz1OMI/w+XgaHUM7NVy9Vz1zuVu4c8ouo6W1DU816Xe3/ABYr3Sfr+D+aKjL4TbueK34Z/T+Fvj37kRqrrH6t7ivVrHXr2FXTZ7o+bSfLDjJSk2mn0fNfM8YFm5YomiuNTv7Is25q5E/ky8AxxxLH7kvofOKVbx/eEmJc5q9LfxRPbcw+6/qYDitvmqp+Emfc5aqWjp15RtruMriSUVnLfgzh4fYn/s0zEd/oht5dFvxVzqGDWeLq9bMdMWyPtv1n4L+X9dDX0W49VZmceqr8NjpHf19lTq7qkm6jbb5tvm3495101a8lL+JMzzTPVOcFaTdS1mnWhFqlHdmT5J5hJcu/mzzfvRyTT6r3hFq7Vdi5y+GPV0gr2pAAAAAAAAAAAAAAAAAAAAAAKjxPwDputZna/wAGs+e6K9CT+1H81h+JZYnFLtjwz4qe32c1zFoqncdJck4i4e1Th+tjUqeIt4jUjzpy8Jdj9zw/caPHzLWRHgnr29Sixpm4fjuspP7b+kT7cq1OnDxCuLdcUz2dC4E0m+jqKr1Ybaai0m+Tee5dq95S8SyLc0fh0z12+4Nmrn59dE9xZZ3dZxnax3KKaeOq593aZu9Yi5MTKPi1m9Vy1243ERO+6m1Jua9I9WrcUTHLDLX7s1W52+2en3N/V22kXJ9vcvF9h28+nNi417Iq5bdO/ot2kcI21tiV/ipPu/kXw/m+PyPNV2fRr8Lglu1qq94p/T+VlSUVhdCJexGn0AAAAAAAAAAAAAAAAAAAAAAAAx3FCjc0XC5jGUJLDjJJxa7mn1PtNU0zuJ6iE0vg7RNKuJStKXWW5Rk90Yvl6qfTp78dmDquZ165Ty1ShuY9u5ci7XG5iNJ85EwBG6hoVhf1N1aOJdri8N+Pf9Q4MrhmPkTuunr+XTfxbttb0bWko28VGK7Eg67Vmi1Ty241DKEgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGOvWjQinPtajy75SSX92B9rVYUaTlVeIpZbfYkBpy1LzcN1alVjT6uclHCXe4qTlFeMeXbjDAy17x07jZSpzm9qk9u3CTbS9aS7mB4eow8zmMJuSkoOHJSUnh4eWl0aec9GB6d7KnbzncUqkIwi5POx5STbwoyfPkBmjcUZW3nFJbNu7c+SxjOfdyAjb/iKysNOoVq6nsr1KdOHo+lurPENyeNvv7gIzU+OtP07V61u6F3UnRUXUdG3lUhBTjui249FjP9L7gMl5xzo9Cxtqlp524/aU3Rhb03OpNR9d7eW1RzzzjHwYGT98LKGi/tNzRuaUfOxouFWi4VFOcoxXot81mS5p/QCR1HWbXT9StqNxu33EpRp4XLMIOby88uSA+aLrlhrcKrsJZdKrOjUT5OM6cmmmu54yn2pgNG1yw1t1v/AM6W5UarozfZvjGLlh9qW5LPemBJAAAAAAAAAAAAAAAAAGnqr22yb6KpTb8FUjkDHeVYXls1aPdKLjPauTeycZYy+XPbj4gep6nQdL+CpSm+kNslLPYmmvQXveEBq21peW9eMaE4rbQpwcpQclJxclyxKOP79QMeypGzzcSlGo6ydSUY8lJJLMU01s2qOOvJ8+eQMt1ONXSa8aVSVWTpzxlLPqtYW2KyBmlY1Xc7U15hy841nnuzlxxj1XL03z6prmpcgrHGdrc1+HbBUYTlKN5bSkoxbajGpmTaS5JLqwNGlYcSz8oGqy0SdOjCcbZecr0JzUsUpLNNqUU3HLz15tAYNV4Z0XhvQbC3uXfb6CqbLuzpz3QlNqVTdtUtqm5PEWpcotZ7w06seJNY4EuvOxr3Co3VOpbOrSVO4q0aVSEpehhZfKWHjMsdOwCWnqk+LeNNOlplvcRpWzq1a1StRlTUXOk4Rgty9KWXzx/fngIPSOEdflXvK2gVHbVK95cUbjzikt1vKrmFWmn/ADxTltfbv6rAFn8lWjrQrW/o0qc6dKN9UVJTT501TpKMk36yeHz7QLwAAAAAAAAAAAAAAAAAAAAABoXWs2FpUkrieHFpP0ZYTaTXNLua/qXegMMuIdLgnvqNYxnNOaaz05bevuA9rXNPlu2TbcVlpRlnGUspNc16Ufmu8DH+8emOSVObbaysRkuXflpID1+8GmujKUZtqKTeITyk5bem3PV9OuOYHqGu6bOqoxqc3JQXoyw5ScklnGOeyXyAkgAAAAAAAAAAAAAAAAAAAAAAAAAA8unBvLSz4frvfzA8uhRc23GOWsN4WWlzx4APMUt7e2OWsN4Wcd3gB8VrbqruUI7sY3bVnDeWs92eeAPfm4dy+QHzzdPuXXPTt7wPYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAf/9k=", 40, height - 200, width - 60, preserveAspectRatio=True, mask='auto')
    # Adicionar título e cabeçalho
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 250, "Relatório de Despesas")
    c.setFont("Helvetica", 12)
    if month is None and year is None:
        import sqlite3

# Conectar ao banco de dados (ou criar um novo se não existir)
        conn = sqlite3.connect('app.db')

# Criar um cursor para executar comandos SQL
        cursor = conn.cursor()

# Executar a consulta para obter a menor data
        cursor.execute("SELECT MIN(date) FROM entry")

# Obter o resultado
        menor_data = cursor.fetchone()[0]

# Exibir a menor data
        print("A menor data é:", menor_data)

# Fechar a conexão
        conn.close()
        month = date.today().month
        year = date.today().year
        
        c.drawString(100, height - 280, f" De {menor_data}  até {month}/{year}")
    else:
       
        c.drawString(100, height - 280, f"Mês: {month}/{year}")
   
    # Adicionar tabela de despesas
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 320, "Data")
    c.drawString(150, height - 320, "Descrição")
    c.drawString(300, height - 320, "Valor")
    c.drawString(400, height - 320, "Categoria")
    c.drawString(500, height - 320, "Tipo")

    c.setFont("Helvetica", 12)
    y = height - 350
    for entry in entries:
        c.drawString(50, y, entry.date.strftime("%d/%m/%Y"))
        c.drawString(150, y, entry.description)
        c.drawString(300, y, f" R$ {entry.amount:.2f}")
        c.drawString(400, y, entry.category)
        c.drawString(500, y, entry.entry_type)
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 50
        day = date.today().day
        month_hoje = date.today().month
        ano_hoje = date.today().year
        c.drawString(100, height - 780, f" Gerado {day}/{month_hoje}/{ano_hoje}, Funcionário responsável,Nome empresa")
    c.save()
    output.seek(0)

    # Definir nome do arquivo PDF
    if month and year:
        file_name = f"{year}-{month}.pdf"
    else:
        file_name = f"{year}.pdf"

    # Enviar o arquivo como resposta de download
    return send_file(output, as_attachment=True, download_name=file_name, mimetype='application/pdf')
