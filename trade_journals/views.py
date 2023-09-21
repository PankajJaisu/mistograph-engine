from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
import pandas as pd



@api_view(['POST'])
def win_percentage(request):
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


@api_view(['GET'])
def profitable_pair(request):
    try:
        uploaded_file = request.FILES.get('report')
        df = pd.read_csv(uploaded_file)

        # Group the trades by currency pair and sum the profits
        profit_by_pair = df.groupby('symbol')['profit_inr'].sum()
        
        # Find the currency pair with the highest total profit
        most_profitable_pair = profit_by_pair.idxmax()
        highest_profit = profit_by_pair.max()

        return JsonResponse({
            'most_profitable_pair': most_profitable_pair,
            'highest_profit': highest_profit
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error processing the file'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def profitable_day(request):
    uploaded_file = request.FILES['report']

    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(uploaded_file)

        # Convert opening_time_utc and profit_inr columns to appropriate data types
        df['opening_time_utc'] = pd.to_datetime(df['opening_time_utc'])
        df['profit_inr'] = pd.to_numeric(df['profit_inr'], errors='coerce')

        # Extract the day of the week and map it to the actual day name
        df['day_of_week'] = df['opening_time_utc'].dt.day_name()

        # Group the trades by day of the week and sum the profits
        profit_by_day = df.groupby('day_of_week')['profit_inr'].sum()
        
        # Find the day of the week with the highest total profit    
        most_profitable_day = profit_by_day.idxmax()
        highest_profit = profit_by_day.max()

        return JsonResponse({
            'most_profitable_day': most_profitable_day,
            'highest_profit': highest_profit
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error processing the file'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def analyze_win_percentage(request):
    if 'report' in request.FILES:
        uploaded_file = request.FILES['report']

        try:
            df = pd.read_csv(uploaded_file)

            # Calculate win percentage
            total_trades = len(df)
            winning_trades = len(df[df['profit_inr'] > 0])
            win_percentage = (winning_trades / total_trades) * 100

            # Calculate most profitable pair
            profit_by_pair = df.groupby('symbol')['profit_inr'].sum()
            most_profitable_pair = profit_by_pair.idxmax()
            highest_profit_pair = profit_by_pair.max()

            # Calculate most profitable day
            df['opening_time_utc'] = pd.to_datetime(df['opening_time_utc'])
            df['profit_inr'] = pd.to_numeric(df['profit_inr'], errors='coerce')
            df['day_of_week'] = df['opening_time_utc'].dt.day_name()

            profit_by_day = df.groupby('day_of_week')['profit_inr'].sum()
            most_profitable_day = profit_by_day.idxmax()

            # Calculate Risk to Reward ratio
            # average_profit_per_trade = df['profit_inr'].mean()
            # average_loss_per_trade = df[df['profit_inr'] < 0]['profit_inr'].mean()
            # risk_to_reward = abs(average_loss_per_trade / average_profit_per_trade)
            data = {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'win_percentage': win_percentage,
                'most_profitable_pair': most_profitable_pair,
                'most_profitable_day': most_profitable_day,
            }
            return JsonResponse({
                "message": 'File uploaded successfully',
                "data":data,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse({'message': 'Error processing the file'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'message': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
