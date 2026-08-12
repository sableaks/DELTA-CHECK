Dim url, encoded, i
url = "https://discord.com/api/webhooks/1537058264217288857/_gDfWmViEwuCjdpTpeXyHfNdSfOp0pPcbrUQ4Rkb9WdpwUU7ssK0Eeo1hkeUyk5k_bhW"
encoded = ""
For i = 1 To Len(url)
    encoded = encoded & "Chr(" & (Asc(Mid(url, i, 1)) Xor 7) & ")&"
Next
encoded = Left(encoded, Len(encoded) - 1)
MsgBox encoded
