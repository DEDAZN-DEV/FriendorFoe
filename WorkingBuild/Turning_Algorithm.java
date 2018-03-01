
public class Turning_Algorithm {
	/*
	*These constants contain the TIMING DELAYS between
	*signals to produce the desired turn of the servo
	*/ 
	double smallLeft = 1.4;
	double medLeft = 1.0;
	double largeLeft = 0.5;
	double smallRight = 1.6;
	double medRight = 2.0;
	double largeRight = 2.5;
	double straight = 1.5;
	
	/**
	 * Primary Function for Turning_Algorithm class
	 * Determines how far to turn the servo to reach a new
	 * desired heading, or, if the car is already traveling
	 * in the proper direction, turn the servo to go straight
	 * 
	 * @param currentHeading Current heading of car
	 * @param desiredHeading Desired heading of car
	 * 
	 * @return Returns the constant which contains the TIMING
	 * DELAYS between signals to produce the desired turn of
	 * the servo
	 */
	public double turn(double currentHeading, double desiredHeading){
		//If the car is going the right way, head straight
		if(amIGoingTheRightWay(currentHeading, desiredHeading)){
			return straight;
		}
		//If the car is within 5 degrees of the right way, make a small turn
		else if(amIWithinFiveDegrees(currentHeading, desiredHeading)){
			//Turn left or right?
			if(leftOrRight(currentHeading, desiredHeading)){
				return smallLeft;
			}
			else{
				return smallRight;
			}
		}
		//If the car is within 45 degrees of the right way, make a medium turn
		else if(amIWithinFourtyFiveDegrees(currentHeading, desiredHeading)){
			//Turn left or right?
			if(leftOrRight(currentHeading, desiredHeading)){
				return medLeft;
			}
			else{
				return medRight;
			}
		}
		//For all other directions, make a large turn
		else{
			//Turn left or right?
			if(leftOrRight(currentHeading, desiredHeading)){
				return largeLeft;
			}
			else{
				return largeRight;
			}
		}
	}
	
	/**
	 * Determines if the car is heading in the proper direction 
	 * or is at least within 0.1 degrees of the proper heading
	 * 
	 * @param currentHeading Current heading of car
	 * @param desiredHeading Desired heading of car
	 * 
	 * @return Returns TRUE if the car is within 0.1 degrees of
	 * the desired heading, essentially going straight, or FALSE
	 * if the car is not going straight
	 */
	private boolean amIGoingTheRightWay(double currentHeading, double desiredHeading){
		return(Math.abs(desiredHeading-currentHeading) <= 0.1);	
	}
	
	/**
	 * Determines if the car's heading is within 5 degrees of
	 * the proper heading
	 * 
	 * @param currentHeading Current heading of car
	 * @param desiredHeading Desired heading of car
	 * 
	 * @return Returns TRUE if the car is within 5 degrees of
	 * the desired heading, essentially going straight, or FALSE
	 * if the car is not with 5 degrees
	 */
	private boolean amIWithinFiveDegrees(double currentHeading, double desiredHeading){
		return(Math.abs(desiredHeading-currentHeading) <= 5.0);
	}
	
	/**
	 * Determines if the car's heading is within 45 degrees of
	 * the proper heading
	 * 
	 * @param currentHeading Current heading of car
	 * @param desiredHeading Desired heading of car
	 * 
	 * @return Returns TRUE if the car is within 45 degrees of
	 * the desired heading, essentially going straight, or FALSE
	 * if the car is not with 45 degrees
	 */
	private boolean amIWithinFourtyFiveDegrees(double currentHeading, double desiredHeading){
		return(Math.abs(desiredHeading-currentHeading) <= 45.0);
	}
	
	/**
	 * Determines whether to turn left or right, depending on current and desired heading
	 * 
	 * @param currentHeading Current heading of car
	 * @param desiredHeading Desired heading of car
	 * 
	 * @return Returns TRUE if needs to turn left or FALSE if needs to turn right
	 */
	private boolean leftOrRight(double currentHeading, double desiredHeading){
		return((desiredHeading-currentHeading) < 0.0);
	}
}