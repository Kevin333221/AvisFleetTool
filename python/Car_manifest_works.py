 # # Function to calculate the score
    # def calculate_score(pickup_time, rental_length):
    #     return pickup_time + (rental_length // SCORE_PER_RENTAL_LENGTH)

    # # Function to get the car group index
    # def get_car_group_index(car_group):
    #     return CAR_GROUP_FILL_ORDER.index(car_group) if car_group in CAR_GROUP_FILL_ORDER else EL_CAR_GROUP_FILL_ORDER.index(car_group)

    # # Iterate through the customers and assign cars
    # for i, customer in enumerate(cleaned_customers):
    #     pickup_time, car_group, rental_length = customer.pickup_time, customer.car_group, customer.rental_length
    #     car_group_index = get_car_group_index(car_group)
    #     group = CAR_GROUP_FILL_ORDER if car_group in CAR_GROUP_FILL_ORDER else EL_CAR_GROUP_FILL_ORDER

    #     # Check if there are available cars in the desired car group
    #     if car_groups_on_hand.get(car_group, 0) > 0:
    #         car_groups_on_hand[car_group] -= 1
    #         customer.assignment = "OK"
    #         customer.score = f"Score: {calculate_score(int(pickup_time), int(rental_length))}"
    #     else:
    #         # Check for possible upgrades
    #         assigned = False
    #         for j in range(car_group_index + 1, len(group)):
    #             upgrade_car_group = group[j]
                
    #             # Check if there are available cars in the desired car group
    #             if car_groups_on_hand.get(upgrade_car_group, 0) > 0:
                    
    #                 for k in range(i + 1, len(cleaned_customers)):
    #                     # print(f"Current: {customer} - Next: {cleaned_customers[k]}")
    #                     next_customer_pickup_time = cleaned_customers[k].pickup_time
    #                     if cleaned_customers[k].car_group in [car_group, upgrade_car_group]:
    #                         current_customer_score = calculate_score(int(pickup_time), int(rental_length))
    #                         next_customer_score = calculate_score(int(next_customer_pickup_time), int(cleaned_customers[k].rental_length))
    #                         if next_customer_score >= current_customer_score + 1000:
    #                             # print(f"Current: {current_customer_score} - Next: {next_customer_score}")
    #                             car_groups_on_hand[upgrade_car_group] -= 1
    #                             customer.assignment = f"Upgrader til {upgrade_car_group}"
    #                             customer.score = f"Score: {calculate_score(int(pickup_time), int(rental_length))}"
    #                             assigned = True
    #                             break
    #                 else:
    #                     car_groups_on_hand[upgrade_car_group] -= 1
    #                     customer.assignment = f"Upgrader til {upgrade_car_group}"
    #                     customer.score = f"Score: {calculate_score(int(pickup_time), int(rental_length))}"
    #                     assigned = True
    #                     break
                    
    #         if not assigned:
    #             customer.assignment = "Mangler"
    #             customer.score = f"Score: {calculate_score(int(pickup_time), int(rental_length))}"                   

    # print("Give these customers the following cars:")
    # for customer in cleaned_customers:
    #     print(customer)