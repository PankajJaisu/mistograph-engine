from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
import pandas as pd



@api_view(['GET'])
def analyze_win_percentage(request):
    print(request.FILES.get('report'))
  
    uploaded_file = request.FILES.get('report')
    try:
     
        df = pd.read_csv(uploaded_file)

        total_trades = len(df)
        winning_trades = len(df[df['profit_inr'] > 0])
        win_percentage = (winning_trades / total_trades) * 100
        return JsonResponse({
                    'message': 'File uploaded successfully',
                    'total_trades': total_trades,
                    'winning_trades': winning_trades,
                    'win_percentage': win_percentage
                }, status=status.HTTP_201_CREATED)
    except Exception as e:
            return JsonResponse({'message': 'Error processing the file'}, status=status.HTTP_400_BAD_REQUEST)

